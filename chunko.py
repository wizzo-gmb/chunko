import os
import argparse
import numpy as np
import librosa
from pydub import AudioSegment
import os
from joblib import Parallel, delayed
from tqdm import tqdm
import warnings
import sys
import soundfile as sf
import io

# Disable librosa warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Add argument parser
parser = argparse.ArgumentParser(description='Audio chunking tool')
parser.add_argument('--input-dir', type=str, required=True, default=r'Input directory of audio')
parser.add_argument('--output-dir', type=str, required=True, default=r'output directory')
parser.add_argument('--chunk-size', type=int, default=196608, help='196608')
parser.add_argument('--overlap', type=int, default=0, help='0')
parser.add_argument('--threshold', type=float, default=-50, help='-50')
parser.add_argument('--num-workers', type=int, default=10, help='5')

args = parser.parse_args()

def chunk_audio(input_file, output_dir, chunk_size, overlap, threshold):
    # Load audio file
    y, sr = librosa.load(input_file, sr=None)

    # Trim silence from beginning and end of audio file
    y_trimmed, _ = librosa.effects.trim(y)

    # Check if the audio file is long enough to be chunked
    if len(y_trimmed) < chunk_size:
        print(f"Skipping {input_file} - file too short")
        return

    # Set frame length and hop length for chunking
    frame_length = chunk_size
    hop_length = frame_length - overlap

    # Chunk audio
    chunks = librosa.util.frame(y_trimmed, frame_length=frame_length, hop_length=hop_length)

    # Check if each chunk meets the volume threshold
    chunk_passes_threshold = np.apply_along_axis(lambda x: np.max(x) >= threshold, axis=0, arr=chunks)

    # Save chunks that pass the threshold
    for i, chunk in enumerate(chunks.T):
        if chunk_passes_threshold[i]:
            output_file = os.path.join(output_dir, os.path.basename(input_file) + f'.chunk{i:02d}.wav')
            sf.write(output_file, chunk, sr)


def process_files(input_dir, output_dir, chunk_size, overlap, threshold, num_workers):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get a list of input files
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]

    # Process the files in parallel
    results = Parallel(n_jobs=num_workers)(delayed(chunk_audio)(f, output_dir, chunk_size, overlap, threshold) for f in tqdm(files))

    return results

def rmempty(files, output_path,threshold):
    for file in files:
        fname = os.path.basename(file)
        audio = AudioSegment.from_file(file)
        loudness = audio.dBFS
        if loudness == float(threshold):
            os.remove(file)
            if output_path:
                output_file = os.path.join(output_path, fname)
                if os.path.exists(output_file):
                    os.remove(output_file)

# Call the process_files function with the command line arguments
files = [os.path.join(args.output_dir, f) for f in os.listdir(args.output_dir) if os.path.isfile(os.path.join(args.output_dir, f))]
process_files(args.input_dir, args.output_dir, args.chunk_size, args.overlap, args.threshold, args.num_workers)

# call the function to remove files that don't meet the DB threshold
rmempty(files, args.output_dir, args.threshold)