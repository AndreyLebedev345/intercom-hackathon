About
Generate videos from reference image(s) and text using Google's Veo 3 model.

The prompt should describe how to animate between the first and last frame. Include:

Action: How the first and last frame should be animated
Style: Desired animation style
Camera motion (optional): How camera should move
Ambiance (optional): Desired mood and atmosphere
More details are available in our prompting guide.

The model supports:

Input images up to 8MB in size
720p or 1080p output resolution
Natural motion and realistic animations
Control over animation via text prompts
Safety filters are applied to both input images and generated content.

1. Calling the API
#
Install the client
#
The client provides a convenient way to interact with the model API.


pip install fal-client
Setup your API Key
#
Set FAL_KEY as an environment variable in your runtime.


export FAL_KEY="YOUR_API_KEY"
Submit a request
#
The client API handles the API submit protocol. It will handle the request status updates and return the result when the request is completed.

PythonPython (async)

import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
           print(log["message"])

result = fal_client.subscribe(
    "fal-ai/veo3.1/reference-to-video",
    arguments={
        "image_urls": ["https://storage.googleapis.com/falserverless/example_inputs/veo31-r2v-input-1.png", "https://storage.googleapis.com/falserverless/example_inputs/veo31-r2v-input-2.png", "https://storage.googleapis.com/falserverless/example_inputs/veo31-r2v-input-3.png"],
        "prompt": "A graceful ballerina dancing outside a circus tent on green grass, with colorful wildflowers swaying around her as she twirls and poses in the meadow."
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)
print(result)
2. Authentication
#
The API uses an API Key for authentication. It is recommended you set the FAL_KEY environment variable in your runtime when possible.

API Key
#
Protect your API Key
When running code on the client-side (e.g. in a browser, mobile app or GUI applications), make sure to not expose your FAL_KEY. Instead, use a server-side proxy to make requests to the API. For more information, check out our server-side integration guide.

3. Queue
#
Long-running requests
For long-running requests, such as training jobs or models with slower inference times, it is recommended to check the Queue status and rely on Webhooks instead of blocking while waiting for the result.

Submit a request
#
The client API provides a convenient way to submit requests to the model.

PythonPython (async)

import fal_client

handler = fal_client.submit(
    "fal-ai/veo3.1/reference-to-video",
    arguments={
        "image_urls": ["https://storage.googleapis.com/falserverless/example_inputs/veo31-r2v-input-1.png", "https://storage.googleapis.com/falserverless/example_inputs/veo31-r2v-input-2.png", "https://storage.googleapis.com/falserverless/example_inputs/veo31-r2v-input-3.png"],
        "prompt": "A graceful ballerina dancing outside a circus tent on green grass, with colorful wildflowers swaying around her as she twirls and poses in the meadow."
    },
    webhook_url="https://optional.webhook.url/for/results",
)

request_id = handler.request_id
Fetch request status
#
You can fetch the status of a request to check if it is completed or still in progress.

PythonPython (async)

status = fal_client.status("fal-ai/veo3.1/reference-to-video", request_id, with_logs=True)
Get the result
#
Once the request is completed, you can fetch the result. See the Output Schema for the expected result format.

PythonPython (async)

result = fal_client.result("fal-ai/veo3.1/reference-to-video", request_id)
4. Files
#
Some attributes in the API accept file URLs as input. Whenever that's the case you can pass your own URL or a Base64 data URI.

Data URI (base64)
#
You can pass a Base64 data URI as a file input. The API will handle the file decoding for you. Keep in mind that for large files, this alternative although convenient can impact the request performance.

Hosted files (URL)
#
You can also pass your own URLs as long as they are publicly accessible. Be aware that some hosts might block cross-site requests, rate-limit, or consider the request as a bot.

Uploading files
#
We provide a convenient file storage that allows you to upload files and use them in your requests. You can upload files using the client API and use the returned URL in your requests.

PythonPython (async)

url = fal_client.upload_file("path/to/file")
Read more about file handling in our file upload guide.

5. Schema
#
Input
#
image_urls list<string>
URLs of the reference images to use for consistent subject appearance

prompt string
The text prompt describing the video you want to generate

duration DurationEnum
The duration of the generated video in seconds Default value: "8s"

Possible enum values: 8s

resolution ResolutionEnum
Resolution of the generated video Default value: "720p"

Possible enum values: 720p, 1080p

generate_audio boolean
Whether to generate audio for the video. If false, %33 less credits will be used. Default value: true


{
  "image_urls": [
    "https://storage.googleapis.com/falserverless/example_inputs/veo31-r2v-input-1.png",
    "https://storage.googleapis.com/falserverless/example_inputs/veo31-r2v-input-2.png",
    "https://storage.googleapis.com/falserverless/example_inputs/veo31-r2v-input-3.png"
  ],
  "prompt": "A graceful ballerina dancing outside a circus tent on green grass, with colorful wildflowers swaying around her as she twirls and poses in the meadow.",
  "duration": "8s",
  "resolution": "720p",
  "generate_audio": true
}
Output
#
video File
The generated video


{
  "video": {
    "url": "https://storage.googleapis.com/falserverless/example_outputs/veo31-r2v-output.mp4"
  }
}
Other types
#
File
#
url string
The URL where the file can be downloaded from.

content_type string
The mime type of the file.

file_name string
The name of the file. It will be auto-generated if not provided.

file_size integer
The size of the file in bytes.

file_data string
File data

