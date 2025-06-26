import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # For each variable in the crossword
        for var in self.crossword.variables:
            
            # Create a set of words to remove from the variable's domain
            words_to_remove = set()
            
            # Check each word in the current domain
            for word in self.domains[var]:
                # If the word's length does not match the variable's required length
                if len(word) != var.length:
                    words_to_remove.add(word)
            
            # Remove all inconsistent words found
            for word in words_to_remove:
                self.domains[var].remove(word)
                
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlap = self.crossword.overlaps[x, y]

        # If there is no overlap, no revision needed
        if overlap is None:
            return False

        i, j = overlap

        for x_val in self.domains[x].copy():
            found_match = False
            for y_val in self.domains[y]:
                # Check if the characters at the overlap position are the same
                if x_val[i] == y_val[j]:
                    found_match = True
                    break
            if not found_match:
                self.domains[x].remove(x_val)
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        
        # Initialize the queue of arcs
        if arcs is None:
            queue = []
            for var1 in self.crossword.variables:
                for var2 in self.crossword.neighbors(var1):
                    queue.append((var1, var2))
        else:
            queue = list(arcs)

        # Process the queue until it is empty
        while queue:
            x, y = queue.pop(0)

            # If a revision was made to the domain of x
            if self.revise(x, y):
                # If the domain of x is now empty, then no solution is possible
                if not self.domains[x]:
                    return False
                # Add all neighboring arcs of x (excluding y) back to the queue
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return all(v in assignment for v in self.crossword.variables)


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # 1. Check for uniqueness of all values (words)
        words = list(assignment.values())
        if len(words) != len(set(words)):
            return False

        # 2. Check for length and overlap consistency
        for var, word in assignment.items():
            # Check if the word's length matches the variable's required length
            if var.length != len(word):
                return False

            # Check for conflicts with neighboring variables
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    neighbor_word = assignment[neighbor]
                    i, j = self.crossword.overlaps[var, neighbor]
                    # If characters at the overlap position do not match
                    if word[i] != neighbor_word[j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        scores = []
        
        # For each possible word for the current variable
        for word_x in self.domains[var]:
            eliminated_count = 0
            # Check against each unassigned neighbor
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    # Count how many of the neighbor's possible words are ruled out
                    for word_y in self.domains[neighbor]:
                        if word_x[i] != word_y[j]:
                            eliminated_count += 1
            scores.append((eliminated_count, word_x))

        # Sort words by the number of values they rule out (ascending)
        return [word for score, word in sorted(scores)]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_vars = [
            var for var in self.crossword.variables
            if var not in assignment
        ]

        # Sort by domain size (ascending) and then by degree (descending)
        unassigned_vars.sort(
            key=lambda var: (len(self.domains[var]), -len(self.crossword.neighbors(var)))
        )

        return unassigned_vars[0] if unassigned_vars else None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Base case: if assignment is complete, return it
        if self.assignment_complete(assignment):
            return assignment

        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)

        # Try each possible value for the selected variable
        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            # Backtrack: remove the assignment if it leads to no solution
            del assignment[var]

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
