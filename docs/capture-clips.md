# Record the first clips

Use a phone or webcam and one small object, such as a block sliding between two guides. Keep the camera still. Pick an angle where a normal pass and an object that slips sideways look different in a single frame.

1. Film a few short clips of normal passes, out-of-position passes, and background motion that should be ignored. Keep the setup the same across those categories so the model has to learn the event itself.
2. Record a second session later for evaluation. Move the object and restart the recording as you would in practice. Keep frames from a single clip in the same dataset split. Label individual frames by what is visible, since even an abnormal clip will contain normal frames.
3. Put the clips in `data/raw/`. Keep them local while we decide which crops are useful.

## Preview the model input

From the repository root in PowerShell, install the video dependency if needed and preview an MP4.

```powershell
python -m pip install -r ml/requirements.txt
python ml/preview_crops.py data/raw/first-pass.mp4
```

Open `runs/crop-preview/first-pass/preview.png`. The enlarged strip shows the individual 32 × 32 grayscale images saved alongside it. The default crop is centered. If it misses the guide, use `--roi X Y WIDTH HEIGHT` with pixel coordinates measured from the original frame's upper-left corner.

The default samples every tenth frame. For a short event, use `--start 20 --every 1` to inspect consecutive frames from frame 20 onward. Use a distinct `--output` folder for alternate crops or same-named clips. If the position difference is unclear at 32 × 32, try a tighter crop or pass `--size 64` to see whether added detail helps.

The first set is a check of framing and labels. Use additional independent passes and sessions for training and evaluation.
