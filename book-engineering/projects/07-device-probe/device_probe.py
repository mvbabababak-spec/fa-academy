"""Read-only educational PyTorch device probe. TPU is not checked."""
import sys


def detect(torch):
    if torch is None:
        return 'unavailable', 'PyTorch is not installed'
    if torch.cuda.is_available():
        hip = getattr(torch.version, 'hip', None)
        return 'cuda', ('ROCm/HIP build' if hip else 'CUDA build')
    mps = getattr(torch.backends, 'mps', None)
    if mps is not None and mps.is_available():
        return 'mps', 'Apple Metal GPU backend'
    return 'cpu', 'No supported GPU backend detected'


def main():
    try:
        import torch
    except ImportError:
        torch = None
    device, explanation = detect(torch)
    print('python=', sys.version.split()[0])
    print('torch=', getattr(torch, '__version__', 'not installed'))
    print('device=', device)
    print('reason=', explanation)
    print('tpu=not checked')
    if torch is not None:
        x = torch.tensor([1.0, 2.0, 3.0], device=device)
        y = x * 2
        assert y.cpu().tolist() == [2.0, 4.0, 6.0]
        print('result=', y.cpu().tolist())


if __name__ == '__main__':
    main()
