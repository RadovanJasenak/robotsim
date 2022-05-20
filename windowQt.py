from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QHBoxLayout,
    QLabel, QVBoxLayout, QWidget, QLineEdit, QFormLayout
)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtOpenGL import QOpenGLVersionProfile
from PyQt6.QtGui import QSurfaceFormat
import sys

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

import mesh_loader as ml
from robot import Robot
import pyrr


class Window(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("RobotSim")

        # widgets
        self.ogl_widget = OpenGLWidget()
        wheels = self.ogl_widget.robot.number_of_wheels

        spd_labels = []
        spd_input_fields = []
        rot_labels = []
        rot_input_fields = []

        for wheel in range(0, wheels):
            spd_labels.append(QLabel(f"joint rotation speed: {wheel}"))
            spd_input_fields.append(QLineEdit())
            rot_labels.append(QLabel(f"joint rotation PRY: {wheel}"))
            input_fields = []
            for x in range(0, 3):
                input_fields.append(QLineEdit())
                if x == 0:
                    input_fields[x].setPlaceholderText("P")
                if x == 1:
                    input_fields[x].setPlaceholderText("R")
                if x == 2:
                    input_fields[x].setPlaceholderText("Y")
            rot_input_fields.append(input_fields)

        self.pos_label = QLabel("Position: x = 2345 y = 354 y = 234 t = 235")
        apply_button = QPushButton("Apply Changes")
        apply_button.clicked.connect(self.apply_button_func)

        sidebar_container = QWidget()
        sidebar_container.setMaximumWidth(250)

        main_container = QWidget()

        # layouts
        form_layout = QFormLayout()
        column_layout = QVBoxLayout()
        rot_column_layout = QVBoxLayout()
        main_row = QHBoxLayout()

        # place widgets in layouts
        for x in range(0, wheels):
            form_layout.addRow(spd_labels[x], spd_input_fields[x])

        for x in range(0, len(rot_labels)):
            rot_column_layout.addWidget(rot_labels[x])
            rot_column_layout.addWidget(rot_input_fields[x][0])
            rot_column_layout.addWidget(rot_input_fields[x][1])
            rot_column_layout.addWidget(rot_input_fields[x][2])
        form_layout.addRow(rot_column_layout)

        column_layout.addWidget(self.pos_label)
        column_layout.addWidget(apply_button)
        form_layout.addRow(column_layout)

        sidebar_container.setLayout(form_layout)

        main_row.addWidget(self.ogl_widget)
        main_row.addWidget(sidebar_container)

        main_container.setLayout(main_row)

        # set central widget
        self.setCentralWidget(main_container)

    def apply_button_func(self):
        text = "ayaya"
        self.pos_label.setText(text)


class OpenGLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        try:
            if sys.argv[1] is not None:
                filepath = str(sys.argv[1])
                if ".xacro" in filepath:
                    self.robot = Robot(sys.argv[1])
                elif ".urdf" in filepath:
                    self.robot = Robot(sys.argv[1])
                else:
                    self.robot = None
                    raise ValueError

        except ValueError:
            sys.exit("URDF or XACRO file expected")

    def initializeGL(self):
        # set OpenGL version and profile
        self.fmt = QOpenGLVersionProfile()
        self.fmt.setVersion(3, 3)
        self.fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)

        # create openGL vertex and fragment shader
        self.shader = self.create_shader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.shader)

        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_DEPTH_TEST)

        # create perspective projection matrix
        self.projection = pyrr.matrix44.create_perspective_projection(
            fovy=45.0, aspect=1280 / 720,
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

        for link in self.robot.links:
            link.load_mesh()

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

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # refresh screen
        glUseProgram(self.shader)  # here to make sure the correct one is being used

        # draw light & ground
        self.scene.draw_scene(self.model_location)

        # draw robot
        self.robot.base_link.draw(self.model_location, pyrr.matrix44.create_identity())

    def resizeGL(self, w: int, h: int):
        glViewport(0, 0, w, h)
        projection_on_resize = pyrr.matrix44.create_perspective_projection(
            fovy=45.0, aspect=w / h,
            near=0.1, far=100.0)
        glUniformMatrix4fv(self.projection_location, 1, GL_FALSE, projection_on_resize)


class Scene:
    def __init__(self):
        self.ground = ml.MeshLoader("models/plane.obj", [0.412, 0.412, 0.412, 1.0])
        self.ground_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([10.0, 10.0, 10.0]))
        self.ground_position = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0]))
        self.ground_model = pyrr.matrix44.multiply(self.ground_scale, self.ground_position)

        self.light = Light([0., 3., 1.], [1., 1., 1.])

    def draw_scene(self, model_location):
        glUniformMatrix4fv(model_location, 1, GL_FALSE, self.ground_model)
        glBindVertexArray(self.ground.vao)  # bind the VAO that is being drawn
        glDrawArrays(GL_TRIANGLES, 0, self.ground.vertex_count)

    def destroy(self):
        self.ground.destroy()


class Light:
    def __init__(self, position, color):
        self.position = pyrr.Vector3(position)
        self.color = pyrr.Vector3(color)
