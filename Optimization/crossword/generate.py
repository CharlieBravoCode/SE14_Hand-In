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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        for d in self.domains:
            for v in self.domains[d].copy():
                if len(v) != d.length:
                    self.domains[d].remove(v)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        # Get the overlap between the variables
        overlap = self.crossword.overlaps[x, y]

        # If there is no overlap, return False
        if not overlap:
            return False
        
        # If there is an overlap, get the position of the overlapping letters
        overlap_pos_x = overlap[0]
        overlap_pos_y = overlap[1]

        # Kepp track of values to remove
        to_remove = []

        # Check each word in x against each word in y, and if the overlap is not the same letter, remove the word
        for val_x in self.domains[x]:
            overlaps = False
            for val_y in self.domains[y]:
                # If the word is different but the letter in the overlap position is the same, mark x as overlapping
                if val_x != val_y and val_x[overlap_pos_x] == val_y[overlap_pos_y]:
                    overlaps = True
                    break
            # If x does not overlap with anything, remove it
            if not overlaps:
                to_remove.append(val_x)

        if len(to_remove) > 0:
            self.domains[x] = self.domains[x].difference(to_remove)

        # Return True if any values were removed from the domain of x; return False otherwise
        return len(to_remove) > 0
            

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Create a queue of arcs to process
        queue = []
        if arcs is None:
            # Add all arcs to the queue
            for var1 in self.domains:
                for var2 in self.crossword.neighbors(var1):
                    queue.append((var1, var2))
        else:
            # Add the given arcs to the queue
            queue = arcs.copy()

        # Keep processing arcs until the queue is empty
        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                # Check if the domain of variable x is empty
                if not self.domains[x]:
                    return False
                # Add arcs (z, x) to the queue for all z that are neighbors of x and not y
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))

        # All domains are non-empty, so arc consistency has been enforced
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        # Check if all variables have been assigned
        for d in self.domains:
            if d not in assignment:
                return False
        return True


    def consistent(self, assignment):
        """
        Return True if the words in `assignment` fit into the crossword puzzle without conflicting characters,
        and return False otherwise.
        """

        # Create a list to keep track of used words
        used_values = []

        # Check each variable in the assignment
        for var, val in assignment.items():

            # Check if the word has already been used
            if val in used_values:
                return False

            # Check if the length of the word matches the length of the variable
            elif var.length != len(val):
                return False

            # Mark the value as used
            else:
                used_values.append(val)

            # Check for conflicts with neighbors
            for n in self.crossword.neighbors(var):
                if n in assignment:
                    overlap = self.crossword.overlaps[var, n]

                    # Check if the characters in the overlap match
                    if assignment[n][overlap[1]] != val[overlap[0]]:
                        return False
        return True



    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Create a dictionary of values and the number of constraints they rule out
        values = {}

        # For each value in the domain of the variable var that is not already assigned 
        for v in self.domains[var]:
            if v not in assignment:
                constraints = 0

                # Check how many of the neighbors' values it rules out
                for n in self.crossword.neighbors(var):

                    # Get the overlap position
                    overlap = self.crossword.overlaps[var, n]

                    # For each value of the neighbors' domain
                    for n_val in self.domains[n]:

                        # Check if the letter is different and if so increase the count
                        if v[overlap[0]] != n_val[overlap[1]]:
                            constraints += 1
                values[v] = constraints

        # Return sorted
        return sorted(values, key = lambda c: values[c])




    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Create a list of candidates
        candidates = []

        # For all the variables in the domain, create a list of all the variables that are not in the assignment
        for var in self.domains:
            if var not in assignment:

                # Keep track of the domain size and the degree
                candidates.append({
                    'variable': var,
                    'domain_size': len(self.domains[var]),
                    'degree': len(self.crossword.neighbors(var))
                })

        # If there are candidates, return the first sorted by domain size and degree
        if candidates:
            return sorted(candidates, key = lambda v: (v["domain_size"], -v["degree"]))[0]["variable"]

        return None




    def backtrack(self, assignment):

        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
                
        # Check if assignment is complete
        if self.assignment_complete(assignment):
            return assignment

        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)

        # Check if there are no unassigned variables left
        if var is None:
            return None

        # Get the values from those possible, in order
        for val in self.order_domain_values(var, assignment):
            assignment[var] = val

            # If the assignment is consistent, recursively call this function
            if self.consistent(assignment):
                result = self.backtrack(assignment)

                # If the assignment returned a result, return it, otherwise remove the word from the list
                if result:
                    return result
                assignment.pop(var)

        # If no value works, backtrack
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
