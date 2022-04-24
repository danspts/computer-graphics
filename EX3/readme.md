Notes about the added Jupyter Notebook:

As the call to render_scene in scene 6 did not include ambience, and in order to prevent moving ambient to the end of the non-defult arguments in all calls,
we added ambience to the values returned from your_own_scene and added ambient argument to the call of render_scene in scene 6.
We hope that this change will be accepted, as it is impossible to run the original notebook without changing anything

We implemented refraction, Blinn-Phong and the obj reader.

The type of the reflection function can be chosen by an enum option or alteratively by the render_scene_blinn overloader as requested

