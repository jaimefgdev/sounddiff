# Installation

## From PyPI

```sh
pip install sounddiff
```

## From source

```sh
git clone https://github.com/systemblueteam/sounddiff.git
cd sounddiff
pip install -e ".[dev]"
```

## System dependencies

sounddiff uses [libsndfile](http://www.mega-nerd.com/libsndfile/) for audio I/O. It's included in the `soundfile` Python package on most platforms, but you may need to install it separately:

**macOS:**
```sh
brew install libsndfile
```

**Ubuntu/Debian:**
```sh
sudo apt-get install libsndfile1
```

**Windows:** Included automatically via pip.

## Optional: ffmpeg

Core formats (WAV, FLAC, OGG, AIFF) work out of the box. For MP3, AAC, and other compressed formats, install [ffmpeg](https://ffmpeg.org/):

```sh
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg
```

## Shell completions

sounddiff uses [click](https://click.palletsprojects.com/) which supports shell completions:

```sh
# bash
eval "$(_SOUNDDIFF_COMPLETE=bash_source sounddiff)"

# zsh
eval "$(_SOUNDDIFF_COMPLETE=zsh_source sounddiff)"

# fish
_SOUNDDIFF_COMPLETE=fish_source sounddiff | source
```

Add the appropriate line to your shell profile for persistent completions.
