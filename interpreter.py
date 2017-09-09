import operator
from ast import literal_eval

code_page  = '''................................ !"#$%&'()*+,-./0123456789:;<=>?'''
code_page += '''@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~.'''
code_page += '''................................................................'''
code_page += '''................................................................'''

modifiers = ''

def vectorizeDyad(function):
	def inner(a, b):
		A = isinstance(a, list)
		B = isinstance(b, list)
		if A and B:
			return [function(a[i], b[i]) if i < len(a) and i < len(b) else a[i] if i < len(a) else b[i] for i in range(max(len(a), len(b)))]

def advance(pointer, grid):
	if pointer[2] == 0:
		pointer[1] += 1
	elif pointer[2] == 1:
		pointer[0] += 1
	elif pointer[2] == 2:
		pointer[1] -= 1
	elif pointer[2] == 3:
		pointer[0] -= 1
	pointer[0] %= len(grid)
	pointer[1] %= len(grid[pointer[0]])

commands = {
	'+': (vectorizeDyad(operator.add), 2, '-'),
	'-': (vectorizeDyad(operator.sub), 2, '+'),
	',': (lambda: input(), 0, '.'),
	'.': (print, 1, ','),
	'!': (advance, -2, '!'),
}

DO_NOT_INVERT = 1
MAP_OVER_LEFT = 2

def interpret(grid, stack = []):
	if not grid: return stack
	width = max(map(len, grid))
	if not width: return stack
	grid = [row + [' '] * (width - len(row)) for row in grid]
	pointer = [0, 0, 0]
	modifier = 0
	stringmode = False
	string = ''
	escaped = False
	while True:
		command = grid[pointer[0]][pointer[1]]
		if stringmode and (command != '"' or escaped):
			if escaped:
				string += literal_eval('"""' + '\\' + command + '"""')
				escaped = False
			elif command == '\\':
				escaped = True
			else:
				string += command
		elif command == '@':
			return stack
		else:
			modifier_index = modifiers.find(command)
			if modifier_index != -1:
				modifier ^= (1 << modifier_index)
			else:
				numindex = '0123456789'.find(command)
				if numindex != -1:
					stack.append(numindex)
				elif command == '"':
					if stringmode == False:
						stringmode = True
					else:
						stack.append(string)
						string = ''
						stringmode = False
				elif command in commands:
					cmd = commands[command]
					if cmd[1] == -2:
						cmd[0](pointer, grid)
					elif modifier & MAP_OVER_LEFT:
						args = [stack.pop() for i in range(cmd[1] if cmd[1] >= 0 else len(stack))]
						stack.append([cmd[0]([args[0][i]] + args[1:]) for i in range(len(args))])
					else:
						stack.append(cmd[0](*[stack.pop() for i in range(cmd[1] if cmd[1] >= 0 else len(stack))]))
					if not modifier & DO_NOT_INVERT:
						grid[pointer[0]][pointer[1]] = cmd[2]
				modifier = 0
		advance(pointer, grid)

def format_str(output):
	return str(output)

if __name__ == '__main__':
	import sys
	if len(sys.argv) == 1:
		code = []
		while True:
			try:
				code.append(input())
			except KeyboardInterrupt:
				code = code and code[:-1]
				print()
			except EOFError:
				break
		print(format_str(interpret(list(map(list, code)))))
