# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

import torch
import torch.distributed as dist


class Gather(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x: torch.tensor):
        output = [torch.zeros_like(x) for _ in range(dist.get_world_size())]
        dist.all_gather(output, x)
        return tuple(output)

    @staticmethod
    def backward(ctx, *grads):
        all_gradients = torch.stack(grads)
        dist.all_reduce(all_gradients)
        return all_gradients[dist.get_rank()]


def gather(x: torch.tensor):
    if not dist.is_initialized():
        return x
    x_gather = Gather.apply(x)
    x_gather = torch.cat(x_gather, dim=0)
    return x_gather


@torch.no_grad()
def gather_nograd(x: torch.tensor):
    if not dist.is_initialized():
        return x
    x_gather = [torch.ones_like(x) for _ in range(dist.get_world_size())]
    dist.all_gather(x_gather, x, async_op=False)

    x_gather = torch.cat(x_gather, dim=0)
    return x_gather


@torch.no_grad()
def varsize_gather_nograd(x: torch.Tensor):
    """gather tensors of different sizes along the first dimension"""
    if not dist.is_initialized():
        return x

    # determine max size
    size = torch.tensor([x.shape[0]], device=x.device, dtype=torch.int)
    allsizes = [torch.zeros_like(size) for _ in range(dist.get_world_size())]
    dist.all_gather(allsizes, size)
    max_size = max([size.cpu().max() for size in allsizes])

    padded = torch.empty(max_size, *x.shape[1:], dtype=x.dtype, device=x.device)
    padded[: x.shape[0]] = x
    output = [torch.zeros_like(padded) for _ in range(dist.get_world_size())]
    dist.all_gather(output, padded)

    output = [tensor[: allsizes[k]] for k, tensor in enumerate(output)]
    output = torch.cat(output, dim=0)

    return output


@torch.no_grad()
def get_varsize(x: torch.Tensor):
    """gather tensors of different sizes along the first dimension"""
    if not dist.is_initialized():
        return [x.shape[0]]

    # determine max size
    size = torch.tensor([x.shape[0]], device=x.device, dtype=torch.int)
    allsizes = [torch.zeros_like(size) for _ in range(dist.get_world_size())]
    dist.all_gather(allsizes, size)
    allsizes = torch.cat(allsizes)
    return allsizes


def get_rank():
    if not dist.is_available():
        return 0
    if not dist.is_initialized():
        return 0
    return dist.get_rank()


def is_main():
    return get_rank() == 0


def get_world_size():
    if not dist.is_initialized():
        return 1
    else:
        return dist.get_world_size()


def barrier():
    if dist.is_initialized():
        dist.barrier()


def average_main(x):
    if not dist.is_initialized():
        return x
    if dist.is_initialized() and dist.get_world_size() > 1:
        dist.reduce(x, 0, op=dist.ReduceOp.SUM)
        if is_main():
            x = x / dist.get_world_size()
    return x


def sum_main(x):
    if not dist.is_initialized():
        return x
    if dist.is_initialized() and dist.get_world_size() > 1:
        dist.reduce(x, 0, op=dist.ReduceOp.SUM)
    return x


def weighted_average(x, count):
    if not dist.is_initialized():
        if isinstance(x, torch.Tensor):
            x = x.item()
        return x, count
    t_loss = torch.tensor([x * count]).cuda()
    t_total = torch.tensor([count]).cuda()
    t_loss = sum_main(t_loss)
    t_total = sum_main(t_total)
    return (t_loss / t_total).item(), t_total.item()




def symlink_force(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e


def save(model, optimizer, scheduler, step, opt, dir_path, name):
    model_to_save = model.module if hasattr(model, "module") else model
    path = os.path.join(dir_path, "checkpoint")
    epoch_path = os.path.join(path, name)  # "step-%s" % step)
    os.makedirs(epoch_path, exist_ok=True)
    cp = os.path.join(path, "latest")
    fp = os.path.join(epoch_path, "checkpoint.pth")
    checkpoint = {
        "step": step,
        "model": model_to_save.state_dict(),
        "optimizer": optimizer.state_dict(),
        "scheduler": scheduler.state_dict(),
        "opt": opt,
    }
    torch.save(checkpoint, fp)
    symlink_force(epoch_path, cp)
    if not name == "lastlog":
        logger.info(f"Saving model to {epoch_path}")


def load(model_class, dir_path, opt, reset_params=False):
    epoch_path = os.path.realpath(dir_path)
    checkpoint_path = os.path.join(epoch_path, "checkpoint.pth")
    logger.info(f"loading checkpoint {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    opt_checkpoint = checkpoint["opt"]
    state_dict = checkpoint["model"]

    model = model_class(opt_checkpoint)
    model.load_state_dict(state_dict, strict=True)
    model = model.cuda()
    step = checkpoint["step"]
    if not reset_params:
        optimizer, scheduler = set_optim(opt_checkpoint, model)
        scheduler.load_state_dict(checkpoint["scheduler"])
        optimizer.load_state_dict(checkpoint["optimizer"])
    else:
        optimizer, scheduler = set_optim(opt, model)

    return model, optimizer, scheduler, opt_checkpoint, step


############ OPTIM


class WarmupLinearScheduler(torch.optim.lr_scheduler.LambdaLR):
    def __init__(self, optimizer, warmup, total, ratio, last_epoch=-1):
        self.warmup = warmup
        self.total = total
        self.ratio = ratio
        super(WarmupLinearScheduler, self).__init__(optimizer, self.lr_lambda, last_epoch=last_epoch)

    def lr_lambda(self, step):
        if step < self.warmup:
            return (1 - self.ratio) * step / float(max(1, self.warmup))

        return max(
            0.0,
            1.0 + (self.ratio - 1) * (step - self.warmup) / float(max(1.0, self.total - self.warmup)),
        )


class CosineScheduler(torch.optim.lr_scheduler.LambdaLR):
    def __init__(self, optimizer, warmup, total, ratio=0.1, last_epoch=-1):
        self.warmup = warmup
        self.total = total
        self.ratio = ratio
        super(CosineScheduler, self).__init__(optimizer, self.lr_lambda, last_epoch=last_epoch)

    def lr_lambda(self, step):
        if step < self.warmup:
            return float(step) / self.warmup
        s = float(step - self.warmup) / (self.total - self.warmup)
        return self.ratio + (1.0 - self.ratio) * math.cos(0.5 * math.pi * s)


def set_optim(opt, model):
    if opt.optim == "adamw":
        optimizer = torch.optim.AdamW(
            model.parameters(), lr=opt.lr, betas=(opt.beta1, opt.beta2), eps=opt.eps, weight_decay=opt.weight_decay
        )
    else:
        raise NotImplementedError("optimizer class not implemented")

    scheduler_args = {
        "warmup": opt.warmup_steps,
        "total": opt.total_steps,
        "ratio": opt.lr_min_ratio,
    }
    if opt.scheduler == "linear":
        scheduler_class = WarmupLinearScheduler
    elif opt.scheduler == "cosine":
        scheduler_class = CosineScheduler
    else:
        raise ValueError
    scheduler = scheduler_class(optimizer, **scheduler_args)
    return optimizer, scheduler


def get_parameters(net, verbose=False):
    num_params = 0
    for param in net.parameters():
        num_params += param.numel()
    message = "[Network] Total number of parameters : %.6f M" % (num_params / 1e6)
    return message


class WeightedAvgStats:
    """provides an average over a bunch of stats"""

    def __init__(self):
        self.raw_stats: Dict[str, float] = defaultdict(float)
        self.total_weights: Dict[str, float] = defaultdict(float)

    def update(self, vals: Dict[str, Tuple[Number, Number]]) -> None:
        for key, (value, weight) in vals.items():
            self.raw_stats[key] += value * weight
            self.total_weights[key] += weight

    @property
    def stats(self) -> Dict[str, float]:
        return {x: self.raw_stats[x] / self.total_weights[x] for x in self.raw_stats.keys()}

    @property
    def tuple_stats(self) -> Dict[str, Tuple[float, float]]:
        return {x: (self.raw_stats[x] / self.total_weights[x], self.total_weights[x]) for x in self.raw_stats.keys()}

    def reset(self) -> None:
        self.raw_stats = defaultdict(float)
        self.total_weights = defaultdict(float)

    @property
    def average_stats(self) -> Dict[str, float]:
        keys = sorted(self.raw_stats.keys())
        if torch.distributed.is_initialized():
            torch.distributed.broadcast_object_list(keys, src=0)
        global_dict = {}
        for k in keys:
            if not k in self.total_weights:
                v = 0.0
            else:
                v = self.raw_stats[k] / self.total_weights[k]
            v, _ = dist_utils.weighted_average(v, self.total_weights[k])
            global_dict[k] = v
        return global_dict


def load_hf(object_class, model_name):
    try:
        obj = object_class.from_pretrained(model_name, local_files_only=True)
    except:
        obj = object_class.from_pretrained(model_name, local_files_only=False)
    return obj


def init_tb_logger(output_dir):
    try:
        from torch.utils import tensorboard

        if dist_utils.is_main():
            tb_logger = tensorboard.SummaryWriter(output_dir)
        else:
            tb_logger = None
    except:
        logger.warning("Tensorboard is not available.")
        tb_logger = None

    return tb_logger
