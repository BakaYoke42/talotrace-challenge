"""Download the three Kokoro assets before offline rendering, or check their cache."""
import argparse

from huggingface_hub import hf_hub_download
import spacy.util


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Check cached files without downloading")
    args = parser.parse_args()
    if not spacy.util.is_package("en_core_web_sm"):
        raise SystemExit("Missing en_core_web_sm: install requirements-tts.txt in .venv-tts")
    for filename in ("config.json", "kokoro-v1_0.pth", "voices/af_heart.pt"):
        hf_hub_download(repo_id="hexgrad/Kokoro-82M", filename=filename, local_files_only=args.check)
        print(f"Ready: {filename}", flush=True)
    print("Kokoro assets and English language model are ready.")


if __name__ == "__main__":
    main()
