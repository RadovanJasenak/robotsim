import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import mesh_loader as ml
from src.robot import Robot
import pyrr


class App:
    # creating and checking glfw window
    def __init__(self, urdfFilepath):

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
        self.shader = self.create_shader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.shader)

        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_DEPTH_TEST)

        # create perspective projection matrix
        self.projection = pyrr.matrix44.create_perspective_projection(
            fovy=45.0, aspect=1280/720,
            near=0.1, far=100.0)

        # view matrix, eye - position of camera cannot be [0, 0, 0], target i am looking at , up vector of the camera
        camera_position = pyrr.Vector3([0, 1, 1])
        self.look_at = pyrr.matrix44.create_look_at(
            camera_position,
            pyrr.Vector3([0, 0, 0]),
            pyrr.Vector3([0, 1, 0]))

        # get the uniform's location from shader
        self.projection_location = glGetUniformLocation(self.shader, "projection")
        self.view_location = glGetUniformLocation(self.shader, "view")
        self.model_location = glGetUniformLocation(self.shader, "model")

        # upload the projection & view matrices to the shader
        glUniformMatrix4fv(self.projection_location, 1, GL_FALSE, self.projection)
        glUniformMatrix4fv(self.view_location, 1, GL_FALSE, self.look_at)

        self.scene = Scene()
        glUniform3fv(glGetUniformLocation(self.shader, "lightColor"), 1, self.scene.light.color)
        glUniform3fv(glGetUniformLocation(self.shader, "lightPos"), 1, self.scene.light.position)
        glUniform3fv(glGetUniformLocation(self.shader, "viewPos"), 1, self.look_at[0])

        self.robot = Robot(urdfFilepath)

        self.main_loop()

    def main_loop(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()  # check for glfw events

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # refresh screen
            glUseProgram(self.shader)  # here to make sure the correct one is being used

            # draw a robot
            # model = pyrr.matrix44.multiply(self.robot.base_link.rotation, self.robot.base_link.position)
            # model = pyrr.matrix44.multiply(self.robot.base_link.scale, model)
            # glUniformMatrix4fv(self.model_location, 1, GL_FALSE, model)
            # glBindVertexArray(self.robot.base_link.mesh.vao)  # bind the VAO that is being drawn
            # glDrawArrays(GL_TRIANGLES, 0, self.robot.base_link.mesh.vertex_count)
            self.draw_robot(self.robot)

            # scene floor plane model
            glUniformMatrix4fv(self.model_location, 1, GL_FALSE, self.scene.ground_model)
            glBindVertexArray(self.scene.ground.vao)  # bind the VAO that is being drawn
            glDrawArrays(GL_TRIANGLES, 0, self.scene.ground.vertex_count)

            glfw.swap_buffers(self.window)  # swap buffers - double buffering
        self.quit()

    def draw_robot(self, robot: Robot):
        model = pyrr.matrix44.multiply(self.robot.base_link.rotation, self.robot.base_link.position)
        model = pyrr.matrix44.multiply(self.robot.base_link.scale, model)
        glUniformMatrix4fv(self.model_location, 1, GL_FALSE, model)
        glBindVertexArray(self.robot.base_link.mesh.vao)  # bind the VAO that is being drawn
        glDrawArrays(GL_TRIANGLES, 0, self.robot.base_link.mesh.vertex_count)

        for link in robot.links:
            for joint in robot.joints:
                if link.name == joint.child.name:
                    model = pyrr.matrix44.multiply(link.rotation, joint.position)
                    print(joint.position)
                    model = pyrr.matrix44.multiply(link.scale, model)
                    glUniformMatrix4fv(self.model_location, 1, GL_FALSE, model)
                    glBindVertexArray(link.mesh.vao)  # bind the VAO that is being drawn
                    glDrawArrays(GL_TRIANGLES, 0, link.mesh.vertex_count)

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
        for link in self.robot.links:
            link.mesh.destroy()
        self.scene.destroy()
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
        self.ground_position = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0]))
        self.ground_model = pyrr.matrix44.multiply(self.ground_scale, self.ground_position)

        self.light = Light([0., 3., 1.], [1., 1., 1.])

    def destroy(self):
        self.ground.destroy()


class Light:
    def __init__(self, position, color):
        self.position = pyrr.Vector3(position)
        self.color = pyrr.Vector3(color)
