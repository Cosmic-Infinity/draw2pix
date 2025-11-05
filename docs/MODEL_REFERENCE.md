# Trained Models Reference

Quick reference for all 15 trained pix2pix models. **Format:** `<Arch>_Flower_<n>.pth` (U256=UNet-256, R9=ResNet-9)

---

## Summary Table

| Model            | Arch | Epochs | Time    | LR      | λ_L1 | BS  | Stability                  |
| ---------------- | ---- | ------ | ------- | ------- | ---- | --- | -------------------------- |
| U256_Flower_1    | U256 | 300    | 14h 4m  | 0.0002  | 100  | 85  | D flatline, G_GAN→4        |
| U256_Flower_2    | U256 | 150    | 2h 31m  | 0.00015 | 100  | 72  | Best D stability           |
| U256_Flower_3    | U256 | 200    | 3h 13m  | 0.0002  | 50   | 70  | Low λ, G_GAN→1.3           |
| U256_Flower_4    | U256 | 250    | 9h 18m  | 0.0001  | 50   | 70  | D collapse, G_GAN→2.5      |
| U256_Flower_5    | U256 | 100    | 3h 44m  | 0.00025 | 65   | 70  | D collapse, G_GAN→2.5      |
| U256_Flower_6    | U256 | 250    | 9h 19m  | 0.00022 | 85   | 70  | Severe collapse, G_GAN→3.5 |
| U256_Flower_7    | U256 | 50     | 1h 53m  | 0.0008  | 85   | 70  | High LR, very noisy        |
| U256_Flower_8    | U256 | 75     | 2h 48m  | 0.0015  | 85   | 70  | Extreme LR, unstable       |
| U256_Flower_9\*  | U256 | 120    | 13h 8m  | 0.0002  | 100  | 1   | BS=1, G_GAN→8              |
| U256_Flower_10\* | U256 | 210    | 22h 18m | 0.0002  | 80   | 1   | BS=1, G_GAN→12             |
| U256_Flower_11   | U256 | 200    | 20h 56m | 0.0004  | 100  | 1   | +Regularization, G_GAN→7.5 |
| U256_Flower_12   | U256 | 200    | 7h 39m  | 0.0003  | 100  | 32  | +Regularization, G_GAN→3.5 |
| R9_Flower_13\*   | R9   | 50     | 7h 15m  | 0.0032  | 100  | 16  | Extreme instability        |
| R9_Flower_14\*   | R9   | 107    | 15h 39m | 0.0002  | 75   | 8   | LSGAN, G_GAN stable~1      |
| U256_Flower_15   | U256 | 200    | 21h 16m | 0.0002  | 100  | 1   | RGB input, G_GAN→15        |

**Notes:** \*=stopped early | Dataset: 12.5k (M1), 9.5k cleaned (M2-15) | All grayscale input except M15 (RGB)

---

## Training Commands

### U256_Flower_1

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG unet_256 --netD basic --input_nc 1 --output_nc 3 --batch_size 85 --no_flip --display_winsize 256 --n_epochs 150 --n_epochs_decay 150 --lr 0.0002 --preprocess none --save_epoch_freq 10 --use_wandb
```

**Time:** 14h 4m | **Loss:** G_L1: 45→12.5, G_GAN: 2→4, D: 0.5→0

### U256_Flower_2

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG unet_256 --netD basic --input_nc 1 --output_nc 3 --batch_size 72 --no_flip --display_winsize 256 --n_epochs 100 --n_epochs_decay 50 --lr 0.00015 --preprocess none --save_epoch_freq 10 --use_wandb
```

**Time:** 2h 31m | **Loss:** G_L1: 45→11, G_GAN: 1.5→1.5, D: ~0.4 stable

### U256_Flower_3

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG unet_256 --netD basic --input_nc 1 --output_nc 3 --batch_size 70 --no_flip --display_winsize 256 --n_epochs 100 --n_epochs_decay 100 --lr 0.0002 --lambda_L1 50 --preprocess none --save_epoch_freq 10 --use_wandb
```

**Time:** 3h 13m | **Loss:** G_L1: 23→5.5, G_GAN: 1.5→1.3, D: 0.6→0.4

### U256_Flower_4

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG unet_256 --netD basic --input_nc 1 --output_nc 3 --batch_size 70 --no_flip --display_winsize 256 --n_epochs 125 --n_epochs_decay 125 --lr 0.0001 --lambda_L1 50 --preprocess none --save_epoch_freq 10 --use_wandb
```

**Time:** 9h 18m | **Loss:** G_L1: 24→7, G_GAN: 1.5→2.5, D: 0.5→0.2

### U256_Flower_5

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG unet_256 --netD basic --input_nc 1 --output_nc 3 --batch_size 70 --no_flip --display_winsize 256 --n_epochs 50 --n_epochs_decay 50 --lr 0.00025 --lambda_L1 65 --preprocess none --save_epoch_freq 10 --use_wandb
```

**Time:** 3h 44m | **Loss:** G_L1: 28→9.5, G_GAN: 2.5→2.5, D: 0.5→0.2

### U256_Flower_6

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG unet_256 --netD basic --input_nc 1 --output_nc 3 --batch_size 70 --no_flip --display_winsize 256 --n_epochs 125 --n_epochs_decay 125 --lr 0.00022 --lambda_L1 85 --preprocess none --save_epoch_freq 10 --use_wandb
```

**Time:** 9h 19m | **Loss:** G_L1: 26→10.5, G_GAN: 2→3.5, D: 0.5→0.1

### U256_Flower_7

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG unet_256 --netD basic --input_nc 1 --output_nc 3 --batch_size 70 --no_flip --display_winsize 256 --n_epochs 50 --n_epochs_decay 0 --lr 0.0008 --lambda_L1 85 --preprocess none --save_epoch_freq 10 --use_wandb
```

**Time:** 1h 53m | **Loss:** G_L1: 38→13.5, G_GAN: 2→2, D: very noisy

### U256_Flower_8

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG unet_256 --netD basic --input_nc 1 --output_nc 3 --batch_size 70 --no_flip --display_winsize 256 --n_epochs 75 --n_epochs_decay 0 --lr 0.0015 --lambda_L1 85 --preprocess none --save_epoch_freq 10 --use_wandb
```

**Time:** 2h 48m | **Loss:** G_L1: 37.5→13.5, G_GAN: 2→3→2.5, D: oscillates 0-1

### U256_Flower_9\* (stopped 120/225)

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG unet_256 --netD basic --input_nc 1 --output_nc 3 --batch_size 1 --no_flip --display_winsize 256 --n_epochs 150 --n_epochs_decay 75 --lr 0.0002 --preprocess none --save_epoch_freq 10 --use_wandb
```

**Time:** 13h 8m | **Loss:** G_L1: 40→20, G_GAN: 3→8, D: 0.5→0 (severe)

### U256_Flower_10\* (stopped 210/225)

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG unet_256 --netD basic --input_nc 1 --output_nc 3 --batch_size 1 --no_flip --display_winsize 256 --n_epochs 150 --n_epochs_decay 75 --lr 0.0002 --lambda_L1 80 --preprocess none --save_epoch_freq 10 --use_wandb
```

**Time:** 22h 18m | **Loss:** G_L1: 33→15, G_GAN: 2.5→12, D: 1→0 (worst)

### U256_Flower_11

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG unet_256 --netD basic --input_nc 1 --output_nc 3 --batch_size 1 --no_flip --display_winsize 256 --n_epochs 100 --n_epochs_decay 100 --lr 0.0004 --preprocess none --save_epoch_freq 10 --use_wandb --use_label_smoothing --instance_noise_std 0.1 --noise_decay
```

**Time:** 20h 56m | **Loss:** G_L1: 40→15, G_GAN: 2.5→7.5, D: 1→0 | **Regularization:** Label smoothing + noise

### U256_Flower_12

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG unet_256 --netD basic --input_nc 1 --output_nc 3 --batch_size 32 --no_flip --display_winsize 256 --n_epochs 100 --n_epochs_decay 100 --lr 0.0003 --preprocess none --save_epoch_freq 20 --use_wandb --use_label_smoothing --instance_noise_std 0.05 --noise_decay
```

**Time:** 7h 39m | **Loss:** G_L1: 43→11, G_GAN: 3→3.5, D: 0.5→0.2 | **Regularization:** Label smoothing + noise

### R9_Flower_13\* (stopped 50/200)

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG resnet_9blocks --netD basic --input_nc 1 --output_nc 3 --batch_size 16 --no_flip --display_winsize 256 --n_epochs 100 --n_epochs_decay 100 --lr 0.0032 --preprocess none --save_epoch_freq 20 --norm instance --use_wandb
```

**Time:** 7h 15m | **Loss:** G_L1: 45→31, G_GAN: 2.5→12.5, D: 0.5→0 | **Arch:** ResNet-9

### R9_Flower_14\* (stopped 107/200)

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --dataset_mode aligned --netG resnet_9blocks --netD basic --norm instance --no_dropout --input_nc 1 --output_nc 3 --batch_size 8 --no_flip --display_winsize 256 --n_epochs 100 --n_epochs_decay 100 --lr 0.0002 --gan_mode lsgan --lambda_L1 75.0 --preprocess resize_and_crop --load_size 286 --crop_size 256 --save_epoch_freq 20 --use_wandb
```

**Time:** 15h 39m | **Loss:** G_L1: 32.5→13, **G_GAN: ~1.0 stable**, D: 0.3→0 | **Best Model** (LSGAN + no dropout)

### U256_Flower_15

```bash
python train.py --dataroot ./datasets/flowers_dataset --name flower --model pix2pix --direction AtoB --use_wandb
```

**Time:** Unknown | **Loss:** G_L1: 42→20, G_GAN: 2.5→15, D: 0.1→0 | **Worst Model** (default params, RGB input)

---

**See also:** `Progress Tracker/Shubham.md` | `docs/TRAINING_REPORT.md` | `docs/ARCHITECTURE.md`
