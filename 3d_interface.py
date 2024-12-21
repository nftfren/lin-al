import sys
import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer
from PySide6.QtGui import QSurfaceFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from pyrr import Matrix44

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0.0
        self.proj = None
        self.view = Matrix44.look_at(
            eye=[3.0, 3.0, 3.0],
            target=[0.0, 0.0, 0.0],
            up=[0.0, 1.0, 0.0]
        )
        self.model = Matrix44.identity()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rotation)
        self.timer.start(16)  # Approximately 60 FPS
        self.init_geometries()

    def init_geometries(self):
        # Initialize coordinate axes
        self.axes = {
            'vertices': np.array([
                # X axis (red)
                0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                1.0, 0.0, 0.0, 1.0, 0.0, 0.0,
                # Y axis (green)
                0.0, 0.0, 0.0, 0.0, 1.0, 0.0,
                0.0, 1.0, 0.0, 0.0, 1.0, 0.0,
                # Z axis (blue)
                0.0, 0.0, 0.0, 0.0, 0.0, 1.0,
                0.0, 0.0, 1.0, 0.0, 0.0, 1.0,
            ], dtype='f4')
        }

        # Initialize cube with all six faces
        self.cube = {
            'vertices': np.array([
                # Front face (cyan)
                -0.5, -0.5,  0.5,  0.0, 1.0, 1.0,
                 0.5, -0.5,  0.5,  0.0, 1.0, 1.0,
                 0.5,  0.5,  0.5,  0.0, 1.0, 1.0,
                -0.5,  0.5,  0.5,  0.0, 1.0, 1.0,

                # Back face (magenta)
                -0.5, -0.5, -0.5,  1.0, 0.0, 1.0,
                 0.5, -0.5, -0.5,  1.0, 0.0, 1.0,
                 0.5,  0.5, -0.5,  1.0, 0.0, 1.0,
                -0.5,  0.5, -0.5,  1.0, 0.0, 1.0,

                # Left face (yellow)
                -0.5, -0.5, -0.5,  1.0, 1.0, 0.0,
                -0.5, -0.5,  0.5,  1.0, 1.0, 0.0,
                -0.5,  0.5,  0.5,  1.0, 1.0, 0.0,
                -0.5,  0.5, -0.5,  1.0, 1.0, 0.0,

                # Right face (green)
                 0.5, -0.5, -0.5,  0.0, 1.0, 0.0,
                 0.5, -0.5,  0.5,  0.0, 1.0, 0.0,
                 0.5,  0.5,  0.5,  0.0, 1.0, 0.0,
                 0.5,  0.5, -0.5,  0.0, 1.0, 0.0,

                # Top face (blue)
                -0.5,  0.5, -0.5,  0.0, 0.0, 1.0,
                -0.5,  0.5,  0.5,  0.0, 0.0, 1.0,
                 0.5,  0.5,  0.5,  0.0, 0.0, 1.0,
                 0.5,  0.5, -0.5,  0.0, 0.0, 1.0,

                # Bottom face (red)
                -0.5, -0.5, -0.5,  1.0, 0.0, 0.0,
                -0.5, -0.5,  0.5,  1.0, 0.0, 0.0,
                 0.5, -0.5,  0.5,  1.0, 0.0, 0.0,
                 0.5, -0.5, -0.5,  1.0, 0.0, 0.0,
            ], dtype='f4')
        }

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        # Additional OpenGL initialization can be done here

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        aspect = w / h if h != 0 else 1
        self.proj = Matrix44.perspective_projection(45.0, aspect, 0.1, 100.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        mvp = self.proj * self.view * self.model

        # Apply the MVP matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(mvp.astype('f4'))

        self.draw_axes()
        self.draw_cube()

    def draw_axes(self):
        glBegin(GL_LINES)
        for i in range(0, len(self.axes['vertices']), 12):
            glColor3f(
                self.axes['vertices'][i + 3],
                self.axes['vertices'][i + 4],
                self.axes['vertices'][i + 5]
            )
            glVertex3f(
                self.axes['vertices'][i],
                self.axes['vertices'][i + 1],
                self.axes['vertices'][i + 2]
            )
            glColor3f(
                self.axes['vertices'][i + 9],
                self.axes['vertices'][i + 10],
                self.axes['vertices'][i + 11]
            )
            glVertex3f(
                self.axes['vertices'][i + 6],
                self.axes['vertices'][i + 7],
                self.axes['vertices'][i + 8]
            )
        glEnd()

    def draw_cube(self):
        glBegin(GL_QUADS)
        for i in range(0, len(self.cube['vertices']), 24):
            for j in range(4):
                vertex_offset = i + j * 6
                glColor3f(
                    self.cube['vertices'][vertex_offset + 3],
                    self.cube['vertices'][vertex_offset + 4],
                    self.cube['vertices'][vertex_offset + 5]
                )
                glVertex3f(
                    self.cube['vertices'][vertex_offset],
                    self.cube['vertices'][vertex_offset + 1],
                    self.cube['vertices'][vertex_offset + 2]
                )
        glEnd()

    def update_rotation(self):
        self.angle += 1.0
        if self.angle >= 360.0:
            self.angle -= 360.0
        self.model = Matrix44.from_y_rotation(np.radians(self.angle))
        self.update()

    def add_geometry(self, vertices):
        # Method to add new geometries
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Interface with Cube")
        self.setGeometry(100, 100, 800, 600)
        self.gl_widget = GLWidget(self)
        self.setCentralWidget(self.gl_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(fmt)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())