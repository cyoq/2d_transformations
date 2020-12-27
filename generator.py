

class Generator:

    i = 0

    def generator(self):
        while True:
            self.i += 1
            yield self.i


gen = Generator().generator()
