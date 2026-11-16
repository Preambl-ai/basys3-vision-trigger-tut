"""Extract and preview grayscale crops from a short video clip."""

import argparse
from pathlib import Path

import cv2


def extract_crops(args):
    video = cv2.VideoCapture(str(args.video))
    try:
        if not video.isOpened():
            raise ValueError(f"could not open video: {args.video}")

        output_dir = args.output or Path("runs/crop-preview") / args.video.stem
        crops = []
        frame_number = 0

        while len(crops) < args.count:
            ok, frame = video.read()
            if not ok:
                break

            if frame_number >= args.start and (frame_number - args.start) % args.every == 0:
                height, width = frame.shape[:2]
                if args.roi:
                    x, y, crop_width, crop_height = args.roi
                else:
                    side = min(width, height) // 2
                    x, y = (width - side) // 2, (height - side) // 2
                    crop_width = crop_height = side

                if (
                    crop_width <= 0 or crop_height <= 0 or x < 0 or y < 0
                    or x + crop_width > width or y + crop_height > height
                ):
                    raise ValueError(f"crop does not fit the {width}x{height} video frame")

                region = frame[y:y + crop_height, x:x + crop_width]
                gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
                crop = cv2.resize(gray, (args.size, args.size), interpolation=cv2.INTER_AREA)
                crops.append((frame_number, crop))

            frame_number += 1
    finally:
        video.release()

    if not crops:
        raise ValueError("no frames selected; check the video and starting frame")

    output_dir.mkdir(parents=True, exist_ok=True)
    previews = []
    for number, crop in crops:
        crop_path = output_dir / f"frame-{number:06d}.png"
        if not cv2.imwrite(str(crop_path), crop):
            raise ValueError(f"could not write {crop_path}")

        preview = cv2.resize(crop, (128, 128), interpolation=cv2.INTER_NEAREST)
        preview = cv2.copyMakeBorder(preview, 20, 0, 0, 0, cv2.BORDER_CONSTANT)
        cv2.putText(preview, f"Frame {number}", (4, 14), cv2.FONT_HERSHEY_SIMPLEX,
                    0.4, 255, 1, cv2.LINE_AA)
        previews.append(preview)

    preview_path = output_dir / "preview.png"
    if not cv2.imwrite(str(preview_path), cv2.vconcat(previews)):
        raise ValueError(f"could not write {preview_path}")
    print(f"Saved {len(crops)} crops. Open {preview_path} to review them.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path, help="input video file")
    parser.add_argument("--size", type=int, choices=(32, 64), default=32)
    parser.add_argument("--roi", type=int, nargs=4, metavar=("X", "Y", "WIDTH", "HEIGHT"),
                        help="crop in source pixels; by default use a centered square")
    parser.add_argument("--start", type=int, default=0, help="starting frame, counted from zero")
    parser.add_argument("--every", type=int, default=10, help="sample every N frames")
    parser.add_argument("--count", type=int, default=8, help="maximum crops to preview")
    parser.add_argument("--output", type=Path, help="directory for the crops and preview")
    args = parser.parse_args()

    if args.start < 0 or args.every < 1 or args.count < 1:
        parser.error("start must be nonnegative and every/count must be positive")
    try:
        extract_crops(args)
    except (ValueError, OSError, cv2.error) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
