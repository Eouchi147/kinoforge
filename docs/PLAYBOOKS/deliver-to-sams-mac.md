# Deliver to Sam's Mac

Only for agents with Sam's Claude desktop connection (device file tools). Every other agent delivers the release link
(`https://github.com/Eouchi147/<repo>/releases/download/<tag>/<asset>`) in its message instead.

## Steps
1. The render has passed `check-before-showing-sam.md`.
2. Download the asset by id into the container (see the check playbook), name it `<series>-<id>[-<style>]-vN.mp4`
   (a re-made film keeps the old file beside it and takes the next suffix: `-v2`, `-v3`).
3. Copy it to the Mac's `Video Production/kino-films/` folder with the device commit tool, then list the folder on the
   device and compare the size with the release asset.
4. If the Mac is disconnected, say so in one line and give the release link; queue the copy for when it returns (note it in
   `docs/STATUS.md` "Waiting").
5. Log: `docs/LOG.md` line ("on Sam's Mac as `kino-films/<file>`"), `docs/STATUS.md`.

## Definition of done
- The file is listed on the Mac with the right size (or Sam has the link and STATUS says the copy is pending); logged.
