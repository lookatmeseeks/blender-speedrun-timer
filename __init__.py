bl_info = {
    "name": "Speedrun Timer",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "category": "3D View",
}


import bpy
import time
import blf


timer_running = False
start_time = 0
original_scene_name = None
draw_handler = None


def draw_timer():

    global timer_running
    global start_time

    font_id = 0

    if timer_running:
        elapsed = time.perf_counter() - start_time

        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        milliseconds = int((elapsed * 1000) % 1000)

        timer_text = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    else:
        timer_text = "00:00.000"

    blf.position(
        font_id,
        50,
        50,
        0
    )

    blf.size(
        font_id,
        32
    )

    blf.color(
        font_id,
        0.1,
        1.0,
        0.1,
        1.0
    )

    blf.draw(
        font_id,
        timer_text
    )


# This is the button action
class SPEEDRUN_OT_start(bpy.types.Operator):
    bl_idname = "speedrun.start"
    bl_label = "Start Run"

    def execute(self, context):

        global timer_running
        global start_time
        global original_scene_name

        if bpy.data.is_dirty:
            print("WARNING: File has unsaved changes!")
            return {'CANCELLED'}

        print("Starting new run...")

        original_scene_name = context.window.scene.name

        # Remove old Speedrun scene if it exists
        if "Speedrun" in bpy.data.scenes:

            old_scene = bpy.data.scenes["Speedrun"]

            # Switch away from it before deleting
            if context.window.scene == old_scene:
                if original_scene_name in bpy.data.scenes:
                    context.window.scene = bpy.data.scenes[original_scene_name]

            bpy.data.scenes.remove(old_scene)
            print("Removed old Speedrun scene.")

        # Create fresh Speedrun scene
        new_scene = bpy.data.scenes.new("Speedrun")

        # Switch to new scene
        context.window.scene = new_scene

        timer_running = True
        start_time = time.perf_counter()

        bpy.app.timers.register(update_timer)

        print("Created and switched to new Speedrun scene.")
        print("Timer started.")

        return {'FINISHED'}


class SPEEDRUN_OT_stop(bpy.types.Operator):
    bl_idname = "speedrun.stop"
    bl_label = "Stop Run"

    def execute(self, context):

        global timer_running

        timer_running = False

        print("Timer stopped.")

        return {'FINISHED'}


class SPEEDRUN_OT_reset(bpy.types.Operator):
    bl_idname = "speedrun.reset"
    bl_label = "Reset Run"

    def execute(self, context):

        global timer_running
        global original_scene_name

        timer_running = False

        if "Speedrun" in bpy.data.scenes:
            speedrun_scene = bpy.data.scenes["Speedrun"]

            if context.window.scene == speedrun_scene:
                if original_scene_name in bpy.data.scenes:
                    context.window.scene = bpy.data.scenes[original_scene_name]

            bpy.data.scenes.remove(speedrun_scene)

            print("Removed Speedrun scene.")

        print("Run reset.")

        return {'FINISHED'}


# This creates the panel
class SPEEDRUN_PT_panel(bpy.types.Panel):
    bl_label = "Speedrun Timer"
    bl_idname = "SPEEDRUN_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Speedrun"

    def draw(self, context):
        layout = self.layout

        if timer_running:
            layout.label(text="Status: RUNNING")
        else:
            layout.label(text="Status: READY")

        layout.operator(
            SPEEDRUN_OT_start.bl_idname
        )

        layout.operator(
            SPEEDRUN_OT_stop.bl_idname
        )

        layout.operator(
            SPEEDRUN_OT_reset.bl_idname
        )


# Register classes with Blender
classes = (
    SPEEDRUN_OT_start,
    SPEEDRUN_OT_stop,
    SPEEDRUN_OT_reset,
    SPEEDRUN_PT_panel,
)


def update_timer():

    global timer_running
    global start_time

    if timer_running:

        # force viewport redraw
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        elapsed = time.perf_counter() - start_time
        print(f"{elapsed:.3f}")

        return 0.1

    return None


def register():

    global draw_handler

    for cls in classes:
        bpy.utils.register_class(cls)

    draw_handler = bpy.types.SpaceView3D.draw_handler_add(
        draw_timer,
        (),
        'WINDOW',
        'POST_PIXEL'
    )


def unregister():

    global draw_handler

    if draw_handler:
        bpy.types.SpaceView3D.draw_handler_remove(
            draw_handler,
            'WINDOW'
        )
        draw_handler = None


    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


    if __name__ == "__main__":
        register()