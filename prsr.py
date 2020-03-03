# -*- coding: utf-8 -*-

import copy

def lexer(text):

    lext = []
    index = 0
    string = ''
    token = ''
    number = ''
    bracket_count = 0

    while index < len(text):
    
        if string:
            if text[index] == '"':
                index = index + 1
                lext.append(("String", string))
                string = ''
                continue
            else:
                string = string + text[index]
                index = index + 1
                continue
        
        if text[index] == '(':
            index = index + 1
            bracket_count = bracket_count + 1
            lext.append(("open_bracket", "("))
            continue
    
        if text[index] == ')':
            if number:
                lext.append(("Number", int(number)))
                number = ''
            if token:
                lext.append(("Function",token))
                token = ''
            index = index + 1
            bracket_count = bracket_count - 1
            if bracket_count < 0:
                print("ERROR: unmatched brackets at {}".format(index))
            lext.append(("close_bracket", ")"))
            continue

        if text[index] =="'" and text[index+1] == "(":
            index = index + 1
            quoted_list = ""
            while text[index] != ")":
                quoted_list = quoted_list + text[index]
                index = index + 1
            quoted_list = quoted_list + ")"
            index = index + 1
            lext.append(("Quoted List", quoted_list))
            continue
            
        if text[index] == '"': # and not quoted is assumed
            index = index + 1
            string = string + text[index]
            index = index + 1
            continue

        if text[index] == ' ':
            if number:
                lext.append(("Number", int(number)))
                number = ''
            if token:
                lext.append(("Function", token))
                token = ''
            index = index + 1
            continue
        
        if text[index].isdigit() and not token:
            number = number + text[index]
            index = index + 1
            continue
        else:
            token = token + text[index]
            index = index + 1

    if number or token or string:
        print("ERROR: Ill formed syntax")
    if bracket_count != 0:
        print("ERROR: unmatched brackets")
    return lext

class node:
    def __init__(self, node_data, parent):
        self.node_data = node_data
        self.child = []
        self.parent = parent
    
    def add_child(self, child_node):
        self.child.append(child_node)
        
    def set_parent(self, parent_node):
        self.parent = parent_node

    def set_node_data(self, node_data):
        self.node_data = node_data
        
    def get_node_data(self):
        return (self.node_data,self.child,self.parent)
        

def debugger(text, candidate, pointer, lext):
    print("{}".format(text))
    print("Candidate {}".format(candidate))
    print("Current Node {}".format(pointer))
    print("lexer list {}".format(lext))
    print()
             
def ast(lexer_list, verbose=False):
    tree = []
    pointer = None
    lext = copy.deepcopy(lexer_list)
    while lext:
        candidate = lext.pop(0)
        if verbose:
            debugger("pop", candidate, pointer, lext)
        if candidate[0] == 'open_bracket':
            tree.append(node(('list', None), pointer))
            if verbose and pointer: debugger("Append open bracket", candidate, pointer, lext)
            if pointer is not None:
                if verbose: debugger("Adding child to parent", candidate, pointer, lext)
                tree[pointer].add_child(len(tree)-1)
                pointer = len(tree) - 1
            else:
                pointer = len(tree) - 1
        if candidate[0] == 'Function':
            if verbose: debugger("updating node to function {}".format(candidate[1]), candidate, pointer, lext)
            tree[pointer].set_node_data(candidate)
            if verbose: debugger("updated node to function {}".format(candidate[1]), candidate, pointer, lext)
            
        if candidate[0] in ('Number', 'String', 'Quoted List'):
            if verbose: debugger("Adding child for {}".format(candidate[1]), candidate, pointer, lext)
            tree.append(node(candidate, pointer))
            if verbose: debugger("Adding child to parent", candidate, pointer, lext)
            tree[pointer].add_child(len(tree)-1)
            
        if candidate[0] == 'close_bracket':
            pointer = tree[pointer].parent
    return tree

def evaluate_ast(tree, position, verbose = False):
    # for each child, if function get return value from recursice call
    params = []
    if verbose: print(position)
    for child in tree[position].get_node_data()[1]:
        if tree[child].get_node_data()[0][0] == "Function":
            params.append(evaluate_ast(tree, child))
        else:
            params.append(tree[child].get_node_data()[0][1])
    if verbose: print("Calling function {} with parameters {}".format(tree[position].get_node_data()[0][1], params))
    return namespace[tree[position].get_node_data()[0][1]](*params)

def evaluate_code(code):
    a = lexer(code)
    b = ast(a)
    return evaluate_ast(b, 0)
        
namespace = {
        'length': lambda x: len(x),
        'largest': lambda x, y: max(x, y),
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y,
        }
  
