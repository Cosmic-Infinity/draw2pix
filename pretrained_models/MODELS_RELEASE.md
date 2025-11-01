To avoid costs associated with git LFS, the models are being distribuetd via github releases.

If you are on windows, simply launching the app from start.bat will prompt you through the downloading the models. </br>
On Mac/Linux, you just have to Download the latest pretained_models.zip from the release, and extract it's contents to pretrained_models directory in the project.

The zip file in the release will consists of 
pretrained_models
  |- model1.pth
  |- model2.pth
  ...
  |-version.txt

  The each new release will be tracked with a version number, which will be present in the version.txt of the release. The auto update setup (Windows only, `via start.bat`) checks the current version, and prompts an update if newer versions exist.
