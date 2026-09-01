# ROS Piper

ROS Piper is a package that integrates the [Piper](https://github.com/rhasspy/piper/) library into a ROS Node.

## Dependencies

### ROS dependencies

- robotnik_common_msgs

### Python dependencies

- piper-tts, numpy, sounddevice

```
pip3 install piper-tts numpy sounddevice
```

> Warning: This step is done manually, as the `piper-tts` package is not available in the ROS repositories.

## Usage

Launch the main node:
```bash
ros2 launch ros_piper piper.launch.xml model_path:=PATH_TO_ONNX_MODEL
```

You may put your voide models in the folder ```resource/models```.

Voice models can be downloaded from https://github.com/rhasspy/piper/blob/master/VOICES.md

### Using different voice models

If the model pointed to by `model_path` is not found locally, the node will try to automatically download it
(along with its `.json` config file) from the [rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices)
repository on Hugging Face.

To use a different voice, set `model_path` to the local destination where you want the model to be stored, using
a file name that matches the one from the piper-voices repository, e.g.:

```bash
ros2 launch ros_piper piper.launch.xml model_path:=$HOME/.config/piper/models/es_ES-davefx-medium.onnx
```

The node derives the download URL from the file name, which must follow the pattern
`{lang}_{COUNTRY}-{name}-{quality}.onnx` (e.g. `es_ES-davefx-medium.onnx`). Browse the available voices at
https://github.com/rhasspy/piper/blob/master/VOICES.md to find the `lang`, `name` and `quality` values for a model.

If the model already exists at `model_path`, it will be used directly without attempting any download.


## Services

### Services provided

- **~/speak** (robotnik_common_msgs/srv/SetString)
Service interface to say something

## Topics

- **~/speak** (std_msgs/msg/String)

Topic interface to say something
