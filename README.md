# ROS Piper

ROS Piper is a package that integrates the [Piper](https://github.com/rhasspy/piper/) library into a ROS Node.

## Dependencies

### ROS dependencies

- robotnik_common_msgs

### Python dependencies

- piper-tts, numpy, sounddevice

```
pip install piper-tts numpy sounddevice
``` 

## Usage

Launch the main node:
```bash
roslaunch ros_piper piper.launch.xml model_path:=PATH_TO_ONNX_MODEL
```

You may put your voide models in the folder ```resource/models```.

Voice models can be downloaded from https://github.com/rhasspy/piper/blob/master/VOICES.md


## Services

### Services provided

- **~/speak** (robotnik_common_msgs/srv/SetString)
Service interface to say something

## Topics

- **~/speak** (std_msgs/msg/String)

Topic interface to say something