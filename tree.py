import networkx as nx

class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.parent = None

class Tree:
    def __init__(self, num_nodes):
        self.d = {}
        self.root = self.create(num_nodes)
    
    def create(self, num_nodes):
        root = TreeNode(0)
        self.d[0] = root
        cur = root
        for i in range(1, num_nodes, 2):
            cur.left = TreeNode(i)
            cur.right = TreeNode(i+1)
            self.d[i] = cur.left
            self.d[i+1] = cur.right
            cur.left.parent = cur
            cur.right.parent = cur
            cur = cur.left
        return root

    def __len__(self):
        return len(self.d)
    
    def remove_subtree(self, u):
        u_node = self.d[u]
    
    def copy_tree(self, u_node):
        root = TreeNode(u_node.val)
        root.left = self.copy_tree(u_node.left)
        root.right = self.copy_tree(u_node.right)
        
    
    def remove_leaf(self, u):
        u_node = self.get_node(u)
        self.d.pop(u)
        parent = u_node.parent
        if u_node == parent.left:
            parent.left = None
        else:
            parent.right = None
    
    def remove_two_children(self, u):
        u_node = self.d[u]
        l_val, r_val = u_node.left.val, u_node.right.val
        self.remove_leaf(l_val)
        self.remove_leaf(r_val)
        return l_val, r_val
        
    def attach_to_leaf(self, leaf, u):
        # attach u to leaf
        u_node = TreeNode(u)
        leaf_node = self.d[leaf]
        if not leaf_node.left:
            leaf_node.left = u_node
        else:
            leaf_node.right = u_node
        u_node.parent = leaf_node
        self.d[u] = u_node
    
    def get_inner_nodes(self):
        return [u for u in self.d if self.d[u].left and self.d[u].parent]
    
    def get_leaves_parents(self):
        parents = []
        leaves = self.get_leaves()
        for u in self.get_inner_nodes():
            u_node = self.get_node(u)
            if u_node.left.val in leaves and u_node.right.val in leaves:
                parents.append(u)
        return parents
    
    def get_leaves(self):
        return [u for u in self.d if not self.d[u].left]
        
    def get_node(self, u):
        return self.d[u]
    
    def get_nodes(self):
        return [self.d[u] for u in self.d]

    def __hash__(self):
        return hash(self.hash_code())
    
    def hash_code(self):
        encode = []
        self.dfs_hash(self.root, encode)
        return ''.join(encode)
    
    def dfs_hash(self, root, encode):
        if not root.left:
            return 
        encode.append('1')
        self.dfs_hash(root.left, encode)
        encode.append('0')
        self.dfs_hash(root.right, encode)
    
    def nx_tree(self):
        tree = nx.DiGraph()
        for u in self.d:
            if self.d[u].left:
                tree.add_edge(u, self.d[u].left.val)
            if self.d[u].right:
                tree.add_edge(u, self.d[u].right.val)
        return tree
    
    def __eq__(self, other):
        return self.hash_code() == other.hash_code()