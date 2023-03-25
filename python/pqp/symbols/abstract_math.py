from abc import ABC, abstractmethod

class AbstractMath(ABC):
    """Abstract class for things that can be displayed as math"""

    @abstractmethod
    def to_latex(self):
        raise NotImplementedError()

    def display(self):
        """Renders an expression as Latex using IPython.display"""
        from IPython.display import display, Math
        return display(Math(self.to_latex()))
