from typing import List, Optional, Tuple

HUMAN = 'X'
AI = 'O'
EMPTY = ' '

WINNING_COMBINATIONS = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]


class Board:
    def __init__(self, state: Optional[List[str]] = None):
        if state is None:
            self.cells = [EMPTY] * 9
        else:
            self.cells = list(state)

    def is_empty(self, index: int) -> bool:
        return self.cells[index] == EMPTY

    def make_move(self, index: int, player: str) -> bool:
        if 0 <= index < 9 and self.cells[index] == EMPTY:
            self.cells[index] = player
            return True
        return False

    def undo_move(self, index: int) -> None:
        if 0 <= index < 9:
            self.cells[index] = EMPTY

    def get_legal_moves(self) -> List[int]:
        return [i for i, cell in enumerate(self.cells) if cell == EMPTY]

    def check_winner(self) -> Tuple[Optional[str], Optional[Tuple[int, int, int]]]:
        for a, b, c in WINNING_COMBINATIONS:
            if self.cells[a] != EMPTY and self.cells[a] == self.cells[b] == self.cells[c]:
                return self.cells[a], (a, b, c)
        return None, None

    def is_full(self) -> bool:
        return EMPTY not in self.cells

    def is_draw(self) -> bool:
        winner, _ = self.check_winner()
        return winner is None and self.is_full()

    def is_terminal(self) -> bool:
        winner, _ = self.check_winner()
        return winner is not None or self.is_full()

    def clone(self) -> 'Board':
        return Board(self.cells)

    def reset(self) -> None:
        self.cells = [EMPTY] * 9
