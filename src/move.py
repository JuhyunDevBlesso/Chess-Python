
class Move:
    def __init__(self,initial,final) -> None:
        #initial and final are squares
        self.initial = initial
        self.final = final

    def __str__(self) -> str:
        s=''
        s +=f'({self.initial.col},{self.initial.row})'
        s +=f'({self.final.col},{self.final.row})'
        return s
    def __eq__(self, value: object) -> bool:
        return self.initial==value.initial and self.final ==value.final