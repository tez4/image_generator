num_lines = 10
filename = "hello.txt"

with open(filename, "w") as f:
    for i in range(num_lines):
        f.write("Hello world!\n")
