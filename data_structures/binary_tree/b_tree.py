class BTree:
    """A B-Tree is a special type of self-balancing tree which acts like
    a BST, except that it may have more than two children.

    B-Trees are ideal for very large trees which are stored on a medium
    which is read sequentially (such as on a hard drive).
    """

    def __init__(self, order, keys=None, parent=None, children=None):
        """Initialize a new BTree with the given values:
            order:    The maximum number of keys in a node in this tree
            keys:     The list of keys for this node (if None, then a
                      new, empty list is made).
            parent:   The parent of this node (or None, if no parent
                      exists)
            children: The list of children for this node (if None, then
                      a new, empty list is made)
        """
        self.order = order
        if keys is None:
            self.keys = []
        else:
            self.keys = keys
        if children is None:
            self.children = []
        else:
            self.children = children
        self.parent = parent
    
    def __contains__(self, value):
        """Search for value in the tree rooted at self, returning
        true if it is found and false otherwise.
        """
        for i in range(len(self.keys)):
            # This is a linear search. Because the keys are sorted, we could
            # do a binary search, which is faster for trees of high order,
            # but either one has the same asymptotic runtime
            if self.keys[i] == value:
                return True
            if self.keys[i] > value:
                if not self.children or self.children[i] is None:
                    return False
                else:
                    return value in self.children[i]
        if not self.children or self.children[-1] is None:
            return False
        else:
            return value in self.children[-1]

    def insert(self, value):
        """Insert a given value into this tree.
        
        Returns True if a value was inserted, and False if it was
        already in the tree.
        """
        if self.children:
            # In an internal node, so find the child and insert
            for i in range(len(self.keys)):
                if self.keys[i] == value:
                    return False
                if self.keys[i] > value:
                    return self.children[i].insert(value)
            return self.children[-1].insert(value)
        else:
            # In a leaf, so insert it into this node
            for i in range(len(self.keys)):
                if self.keys[i] == value:
                    return False
                if self.keys[i] > value:
                    self.keys.insert(i, value)
                    break
            else:
                self.keys.append(value)
            if len(self.keys) > self.order:
                self._insert_median_split()
            return True

    def _insert_median_split(self):
        """A helper method for insert. This splits the node along its
        median and pushes the median up into the parent via
        _insert_recurse.
        """
        median_index = len(self.keys) // 2
        median = self.keys[median_index]
        left = self.keys[:median_index]
        right = self.keys[median_index+1:]
        if self.children:
            left_children = self.children[:median_index+1]
            right_children = self.children[median_index+1:]
        else:
            left_children = None
            right_children = None
        if self.parent is None:
            # We inserted into the root
            self.keys = [median]
            self.children = [BTree(self.order, left, self, left_children),
                             BTree(self.order, right, self, right_children)]
            for child in self.children:
                child._insert_fix_parent_refs()
        else:
            # We need to push the median up a level
            self.parent._insert_recurse(median, left, right)

    def _insert_fix_parent_refs(self):
        """Assign all of ones children to have self as their parent, as
        median splitting may mess up that property.

        A helper method for insert.
        """
        for child in self.children:
            child.parent = self

    def _insert_recurse(self, median, left, right):
            """Replace the child which contains value with two children, one
            containing left and one containing right, separated by median.
            
            left and right are taken to be lists, and turned into BTrees.

            A helper method for insert.
            """
            for i in range(len(self.keys)):
                if self.keys[i] > median:
                    self.keys.insert(i, median)
                    self.children[i:i+1] = [BTree(self.order, left, self),
                                            BTree(self.order, right, self)]
                    break
            else:
                self.keys.append(median)
                self.children[-1:] = [BTree(self.order, left, self),
                                      BTree(self.order, right, self)]
            if len(self.keys) > self.order:
                self._insert_median_split()

    def remove(self, value):
        """Remove a value from the tree, returning True if it was
        removed or False if no such value exists.
        """
        if self.children:
            for i, key in enumerate(self.keys):
                if key == value:
                    pred = self.children[i].maximum()
                    self.keys[i] = pred
                    return self.children[i].remove(pred)
                if key > value:
                    return self.children[i].remove(value)
            return self.children[-1].remove(value)
        else:
            for i, key in enumerate(self.keys):
                if key == value:
                    self.keys.remove(value)
                    if len(self.keys) < self.order // 2:
                        # TODO Rebalance the tree
                        self._remove_rebalance()
                    return True
                if key > value:
                    return False

    def _remove_rebalance(self):
        """Rebalance the tree after removing a value from a node.

        A helper function for remove.
        """
        print(self)
        if self.parent is None:
            # Nothing to do, as there is no other tree part to balance
            return
        if self.left_sibling and self.left_sibling.num_children > self.order:
            self.parent._remove_rotate_right(self)
            return
        elif self.right_sibling and self.right_sibling.num_children >self.order:
            self.parent._remove_rotate_left(self)
            return
        elif self.left_sibling:
            self.parent._remove_combine_left(self)
        else:
            self.parent._remove_combine_left(self.right_sibling)

    def _remove_rotate_left(self, dest):
        """Move a value from dest's right sibling to the separator and
        move the separator into dest.

        A helper function for remove.
        """
        index = self.children.index(dest)
        dest.insert(self.keys[index])
        self.keys[index] = self.children[index+1].minimum()
        self.children[index+1].remove(self.keys[index])

    def _remove_rotate_right(self, dest):
        """Move a vlue from dest's left sibling to the separator and
        move the separator into dest.
        
        A helper function for remove.
        """
        index = self.children.index(dest) - 1
        dest.insert(self.keys[index])
        self.keys[index] = self.children[index].maximum()
        self.children[index].remove(self.keys[index])

    def _remove_combine_left(self, child):
        """Combine the given child node and the node to its left, and
        fold into that the separator.

        A helper function for remove.
        """
        # TODO Check if one is leaf while other isn't
        index = self.children.index(child)-1
        left = self.children[index]
        left.keys.append(self.keys[index])
        left.keys += child.keys
        left.children += child.children
        left._insert_fix_parent_refs()
        del self.keys[index]
        if len(self.keys) < self.order // 2:
            self._remove_rebalance()

    def maximum(self):
        """Return the largest value in the subtree rooted at this vertex."""
        if self.children:
            return self.children[-1].maximum()
        else:
            return self.keys[-1]

    def minimum(self):
        """Return the smallest value in the subtree rooted at this vertex."""
        if self.children:
            return self.children[0].minimum()
        else:
            return self.keys[0]

    @property
    def left_sibling(self):
        if self.parent is None:
            return None
        index = self.parent.children.index(self)
        if index == 0:
            return None
        return self.parent.children[index-1]

    @property
    def right_sibling(self):
        if self.parent is None:
            return None
        index = self.parent.children.index(self)
        if index == self.parent.num_children-1:
            return None
        return self.parent.children[index+1]

    @property
    def num_children(self):
        return len(self.children)

    def __repr__(self):
        from pprint import pformat
        if self.children:
            return pformat({tuple(self.keys): self.children})
        else:
            return pformat(tuple(self.keys))

# Here's tests to ensure that everything works
import unittest

class TestBTree(unittest.TestCase):
    def test_insert_search(self):
        """Test that searching for inserted values works as intended."""
        for order in range(2, 8, 2):
            tree = BTree(order)
            [tree.insert(x) for x in [0, -2, 2, -4, 4, 6, 8, 10]]
            for pos in [0, 2, -2, 10, 6]:
                self.assertEqual(pos in tree, True,
                                 f'{pos} should be in tree, but is not.')
            for neg in [-10, -3, -1, 1, 3, 7, 13]:
                self.assertEqual(neg in tree, False,
                                 f'{neg} should not be in tree, but is.')

    def test_insert_balancing(self):
        tree = BTree(4)
        [tree.insert(x) for x in [0, -2, 2, -4, 4, 6, 8, 10,
                                  -6, -8, -10, 1, 3, 5, 9]]
        self.assertEqual(tree.keys, [-6, 0, 3, 6])
        self.assertEqual(tree.children[0].keys, [-10, -8])
        self.assertEqual(tree.children[1].keys, [-4, -2])
        self.assertEqual(tree.children[2].keys, [1, 2])
        self.assertEqual(tree.children[3].keys, [4, 5])
        self.assertEqual(tree.children[4].keys, [8, 9, 10])
        for child in tree.children:
            self.assertIs(tree, child.parent)
        [tree.insert(x) for x in [-1, -3, -5, -9]]
        self.assertEqual(tree.keys, [0])
        self.assertEqual(tree.children[0].keys, [-6, -3])
        self.assertEqual(tree.children[1].keys, [3, 6])
        for child in tree.children:
            self.assertIs(tree, child.parent)
            for grandchild in child.children:
                self.assertIs(child, grandchild.parent)

    def test_remove_search(self):
        tree = BTree(2)
        [tree.insert(x) for x in [0, -2, 2, -4, 4, 6, 8, 10,
                                  -6, -8, -10, 1, 3, 5, -5]]
        print()
        print(tree)
        # [tree.remove(x) for x in [1, -5, 5, 3]]
        tree.remove(1)
        print(tree)
        tree.remove(-5)
        tree.remove(5)
        tree.remove(3)
        print(tree)
        for pos in [0, 6, -6, 2, 4, 10, 5, 1]:
            self.assertEqual(pos in tree, True,
                             f'{pos} should be in tree.')
        for neg in [1, 3, 5, -5, -13, 13, 7]:
            self.assertEqual(neg in tree, False,
                             f'{neg} should not be in the tree.')

    def test_insert_maximum_minimum(self):
        tree = BTree(4)
        [tree.insert(x) for x in [0, -2, 2, -4, 4, 6, 8, 10]]
        self.assertEqual(10, tree.maximum())
        self.assertEqual(-4, tree.minimum())
        [tree.insert(x) for x in [-6, -8, -10, 1, 3, 5, 9, -1, -3, -5, -9, 15]]
        self.assertEqual(15, tree.maximum())
        self.assertEqual(-10, tree.minimum())

if __name__ == '__main__':
    unittest.main()

