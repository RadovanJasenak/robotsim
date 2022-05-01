import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np
import ctypes
import gui.mesh_loader as ml
from src.robot import Robot
import pyrr


class App:
    # creating and checking glfw window
    def __init__(self, robot: Robot):
        if not glfw.init():
            raise Exception("glfw can not be initialized")
        self.window = glfw.create_window(1280, 720, "RobotSim", None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("glfw window can not be created")

        glfw.set_window_pos(self.window, 400, 200)
        glfw.set_window_size_callback(self.window, self.window_resize)  # window resizing
        glfw.make_context_current(self.window)  # openGL context

        # create openGL shaders, vertex and fragment
        self.shader = self.create_shader("gui/shaders/vertex.txt", "gui/shaders/fragment.txt")
        glUseProgram(self.shader)

        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_DEPTH_TEST)

        # create perspective projection matrix
        self.projection = pyrr.matrix44.create_perspective_projection(
            fovy=45.0, aspect=1280/720,
            near=0.1, far=100.0)

        # view matrix, eye - position of camera cannot be [0, 0, 0], target i am looking at , up vector of the camera
        camera_position = pyrr.Vector3([0, 1, 4])
        self.look_at = pyrr.matrix44.create_look_at(
            camera_position,
            pyrr.Vector3([0, 1, 0]),
            pyrr.Vector3([0, 1, 0]))

        # translate (move) the object in world space
        self.ground_position = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0]))
        self.robot_body_position = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 1, 0]))

        # get the uniform's location from shader
        self.projection_location = glGetUniformLocation(self.shader, "projection")
        self.view_location = glGetUniformLocation(self.shader, "view")
        self.model_location = glGetUniformLocation(self.shader, "model")

        # upload the projection & view matrices to the shader
        glUniformMatrix4fv(self.projection_location, 1, GL_FALSE, self.projection)
        glUniformMatrix4fv(self.view_location, 1, GL_FALSE, self.look_at)

        self.robot_body = ml.MeshLoader("models/cube.obj", robot.base_link.color)
        self.robot_body_scale = pyrr.matrix44.create_from_scale(
            pyrr.Vector3([robot.base_link.length,
                          robot.base_link.height,
                          robot.base_link.width])
        )
        self.scene = Scene()
        self.light = Light([0., 3., 1.], [1., 1., 1.])
        glUniform3fv(glGetUniformLocation(self.shader, "lightColor"), 1, self.light.color)
        glUniform3fv(glGetUniformLocation(self.shader, "lightPos"), 1, self.light.position)
        glUniform3fv(glGetUniformLocation(self.shader, "viewPos"), 1, self.look_at[0])

        self.main_loop()

    def main_loop(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()  # check for glfw events

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # refresh screen
            glUseProgram(self.shader)  # here to make sure the correct one is being used

            rot_x = pyrr.Matrix44.from_x_rotation(0.5 * glfw.get_time())
            rot_y = pyrr.Matrix44.from_y_rotation(0.8 * glfw.get_time())
            rotation = pyrr.matrix44.multiply(rot_x, rot_y)

            # draw a mesh object
            model = pyrr.matrix44.multiply(rotation, self.robot_body_position)
            model = pyrr.matrix44.multiply(self.robot_body_scale, model)
            glUniformMatrix4fv(self.model_location, 1, GL_FALSE, model)
            glBindVertexArray(self.robot_body.vao)  # bind the VAO that is being drawn
            glDrawArrays(GL_TRIANGLES, 0, self.robot_body.vertex_count)

            # scene floor plane model
            model = pyrr.matrix44.multiply(self.scene.ground_scale, self.ground_position)
            glUniformMatrix4fv(self.model_location, 1, GL_FALSE, model)
            glBindVertexArray(self.scene.ground.vao)  # bind the VAO that is being drawn
            glDrawArrays(GL_TRIANGLES, 0, self.scene.ground.vertex_count)

            glfw.swap_buffers(self.window)  # swap buffers - double buffering
        self.quit()

    def create_shader(self, vertexFilepath, fragmentFilepath):
        # load shaders from files and compile them to be used as a program
        with open(vertexFilepath, 'r') as f:
            vertex_src = f.readlines()
        with open(fragmentFilepath, 'r') as f:
            fragment_src = f.readlines()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )
        return shader

    def quit(self):
        # free allocated space before exiting
        glDeleteProgram(self.shader)
        self.robot_body.destroy()
        self.scene.ground.destroy()
        glfw.terminate()

    def window_resize(self, window, width, height):
        # window resizing function
        glViewport(0, 0, width, height)
        projection_on_resize = pyrr.matrix44.create_perspective_projection(
            fovy=45.0, aspect=width/height,
            near=0.1, far=100.0)
        glUniformMatrix4fv(self.projection_location, 1, GL_FALSE, projection_on_resize)


class Scene:
    def __init__(self):
        self.ground = ml.MeshLoader("models/plane.obj", [0.412, 0.412, 0.412, 1.0])
        self.ground_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([10.0, 10.0, 10.0]))
        self.robot = None


# class RobotVisual:
#     def __init__(self, robot: Robot):
#         self.meshes = []
#         for item in robot.links:
#             if item.shape == "box":
#                 self.meshes.append(Mesh("models/cube.obj"))
#             elif item.shape == "cylinder":
#                 self.meshes.append(Mesh("models/cylinder.obj"))
#             elif item.shape == "sphere":
#                 self.meshes.append(Mesh("models/sphere.obj"))
#             else:
#                 raise ValueError("Attempting to draw an object that is not a box, a cylinder or a sphere")
#
#     def create_model(self):
#         # connect the meshes of links with regard to joints
#         pass


class Light:
    def __init__(self, position, color):
        self.position = pyrr.Vector3(position)
        self.color = pyrr.Vector3(color)
