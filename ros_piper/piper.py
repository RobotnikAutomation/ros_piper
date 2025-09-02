# Copyright 2025 Robotnik Automation SL.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from robotnik_common_msgs.srv import SetString
from rcl_interfaces.msg import SetParametersResult

import sys
import os
import numpy as np
import sounddevice as sd
from piper.voice import PiperVoice

from pathlib import Path
import urllib.request
import sys

def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")

    try:
        with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
            total = r.length or 0  # Content-Length may be None
            read = 0
            block = 1024 * 1024  # 1 MiB

            while True:
                chunk = r.read(block)
                if not chunk:
                    break
                f.write(chunk)
                read += len(chunk)
                if total:
                    done = int(50 * read / total)
                    sys.stdout.write(
                        f"\r[{'=' * done}{'.' * (50 - done)}] "
                        f"{read/1024/1024:.1f}/{total/1024/1024:.1f} MB"
                    )
                else:
                    sys.stdout.write(f"\rDownloaded {read/1024/1024:.1f} MB")
                sys.stdout.flush()
        os.replace(tmp, dest)  # atomic move
        print(f"\nSaved: {dest}")
    except Exception as e:
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            pass
        raise RuntimeError(f"Download failed: {e}")

MODEL_NAME = "en_US-john-medium.onnx"
MODEL_CDN = f"https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/john/medium/{MODEL_NAME}"
CONFIG_CDN = f"https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/john/medium/{MODEL_NAME}.json"
LOCAL_DEST = Path.home() / ".config" / "piper" / "models" / "en_US-john-medium.onnx"

class RosPiper(Node):
    def __init__(self):
        super().__init__('ros_piper')
        self.model_path = ""
        self.voice = None
        self.stream = None
        self.add_on_set_parameters_callback(self.parameter_callback)
        self.declare_parameter('model_path', str(LOCAL_DEST))
        
        self.subscription = self.create_subscription(
            String,
            '~/speak',
            self.speak_topic_callback,
            10)
        self.srv = self.create_service(SetString,
            '~/speak',
            self.speak_service_callback)

    def create_model_and_stream(self):
        if self.model_path == "":
            self.get_logger().error('Failed to create model and stream: Model path is empty')
            self.voice = None
            self.stream = None
            return False

        try:
            if not os.path.exists(self.model_path):
                self.get_logger().info(f'Model not found, downloading from {MODEL_CDN}')
                download(MODEL_CDN, LOCAL_DEST)
            if not os.path.exists(f"{LOCAL_DEST}.json"):
                self.get_logger().info(f'Config not found, downloading from {CONFIG_CDN}')
                download(CONFIG_CDN, LOCAL_DEST.with_suffix(LOCAL_DEST.suffix + ".json"))
        except Exception as e:
            self.get_logger().error(f'Error downloading model: {e}')
            return False

        try:
            self.voice = PiperVoice.load(self.model_path)
            self.stream = sd.OutputStream(samplerate=self.voice.config.sample_rate, channels=1, dtype='int16')
            self.get_logger().info(f'Model and stream created successfully with model at: {self.model_path}')
            return True
        except Exception as e:
            self.get_logger().error(f'Error creating model and stream: {e}')
            self.voice = None
            self.stream = None
            return False

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'model_path' and param.type_ == rclpy.Parameter.Type.STRING:
                if self.model_path != param.value:
                    self.model_path = param.value
                    self.get_logger().info('Model path changed to: "%s"' % param.value)
                    if self.create_model_and_stream() == False:
                        self.get_logger().error('Failed to create model and stream')
                        return SetParametersResult(successful=False)
        return SetParametersResult(successful=True)
        

    def speak(self, text):
        self.get_logger().info('I\'m going to say: "%s"' % text)
        if self.voice is None or self.stream is None:
            self.get_logger().error('Voice or stream not initialized')
            return False

        self.stream.start()
        for audio_bytes in self.voice.synthesize_stream_raw(text):
            int_data = np.frombuffer(audio_bytes, dtype=np.int16)
            self.stream.write(int_data)
        self.stream.stop()

        return True

    def speak_service_callback(self, request, response):
        response.response.success = self.speak(request.data)
        if response.response.success == True:
            response.response.message = 'Service called successfully'
        else:
            response.response.message = 'Service failed to call'
        return response

    def speak_topic_callback(self, msg):
        self.speak(msg.data)

    def destroy_node(self):
        if self.stream is not None:
            self.stream.close()  # Ensure the stream is closed
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    ros_piper = RosPiper()

    try:
        rclpy.spin(ros_piper)
    except KeyboardInterrupt:
        pass
    except rclpy.executors.ExternalShutdownException:
        sys.exit(1)
    ros_piper.destroy_node()


if __name__ == '__main__':
    main()
