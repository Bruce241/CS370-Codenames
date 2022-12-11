import random
import time
from gensim.models import Word2Vec, KeyedVectors
from itertools import combinations

model = KeyedVectors.load_word2vec_format(
    'GoogleNews-vectors-negative300.bin.gz', binary=True, limit = 100000)

def get_words(files):
    words = []
    for file in files:
        f = open(file, 'r')
        file_content = f.readlines()
        for line in file_content:
            words.append(line.upper().rstrip())
    game_words = list(random.sample(words, 25))
    return game_words

class Board:
    def __init__(self, words):
        self.words = words
        self.colors = []

        for i in range(13):
            self.colors.append('G')
        for i in range(9):
            self.colors.append('Y')
        for i in range(3):
            self.colors.append('R')
        random.shuffle(self.colors)

        self.guesses = []
    def __str__(self):
        s = ''
        for r in range(5):
            for c in range(5):
                if len(self.words[r*5+c]) < 6:
                    if self.words[r*5+c] in self.guesses:
                        if self.colors[r*5+c] == 'G':
                            if len(self.words[r*5+c]) == 5:
                                s += '| {}✓\t'.format(self.words[r*5+c])
                            else:
                                s += '| {}✓\t\t'.format(self.words[r*5+c])
                        elif self.colors[r*5+c] == 'Y':
                            if len(self.words[r*5+c]) == 5:
                                s += '| {}✗\t'.format(self.words[r*5+c]) 
                            else:
                                s += '| {}✗\t\t'.format(self.words[r*5+c])                    
                    else:
                        s += '| {}\t\t'.format(self.words[r*5+c])
                else:
                    if self.words[r*5+c] in self.guesses:
                        if self.colors[r*5+c] == 'G':
                            s += '| {}✓\t'.format(self.words[r*5+c])
                        elif self.colors[r*5+c] == 'Y':
                            s += '| {}✗\t'.format(self.words[r*5+c])
                    else:
                        s += '| {}\t'.format(self.words[r*5+c])
            s += '|\n'
        s += '\n'
        return s
class Spymaster:
    def __init__(self):
        self.G_words = []
        self.Y_words = []
        self.R_words = []
        self.given_clues = []
    def add_words(self, words, colors):
        self.words = words
        
        for i in range(25):
            if colors[i] == 'G':
                self.G_words.append(words[i].lower())
            if colors[i] == 'Y':
                self.Y_words.append(words[i].lower())
            if colors[i] == 'R':
                self.R_words.append(words[i].lower())
    def get_possible_clues(self):
        possible_clues = []
        combos = []
        
        combos.extend(list(combinations(self.G_words, 1)))
        if(len(self.G_words) >= 2):
            combos.extend(list(combinations(self.G_words, 2)))
        if(len(self.G_words) >= 3):
            combos.extend(list(combinations(self.G_words, 3)))

        #Don't check for assassin words here    
        for combo in combos:
            if len(combo) == 1:
                vec = model[combo[0]] #\
                #- model[self.R_words[0]] - model[self.R_words[1]] - model[self.R_words[2]]
            elif len(combo) == 2:
                vec = model[combo[0]] + model[combo[1]] #\
                #- model[self.R_words[0]] - model[self.R_words[1]] - model[self.R_words[2]]
            elif len(combo) == 3:
                vec = model[combo[0]] + model[combo[1]] + model[combo[2]] #\
                #- model[self.R_words[0]] - model[self.R_words[1]] - model[self.R_words[2]]
                
            similar = model.most_similar([vec])
            num = len(combo)

            #To see which words the AI is giving the clue for
            clue_words = []
            for i in range(num):
                clue_words.append(combo[i])
                
            words_lower = []
            for word in self.words:
                words_lower.append(word.lower())

            #Check if it is a valid clue  
            for clue in similar:     
                if clue[0] not in words_lower:
                    valid = True

                    #Doesn't contain any board words
                    for word in words_lower:
                        if word in clue[0].lower():
                            valid = False
                            break
                        
                    #Wasn't  previously given
                    for word in self.given_clues:
                        if clue[0].lower() in word.lower():
                            valid = False
                            break
                        
                    #Isn't similar to assassin words
                    for word in self.R_words:
                        vec = model[word]
                        similar = model.most_similar([vec], topn=200)
                        for similar_tuple in similar:
                            similar_word = similar_tuple[0]
                            if clue[0].lower() in similar_word or similar_word in clue[0].lower():
                                valid = False
                                break
                        
                    if valid:
                        #Add clue_words here to show which words the AI is giving the clue for
                        the_clue = [clue, num]
                        
                        possible_clues.append(the_clue)
                        break
        return possible_clues
    
    def get_top2_clues(self, possible_clues):
        scores1 = [0]
        scores2 = [0]
        scores3 = [0]

        for clue in possible_clues:
            if clue[1] == 1:
                scores1.append(clue[0][1])
            if clue[1] == 2:
                scores2.append(clue[0][1])
            if clue[1] == 3:
                scores3.append(clue[0][1])
                
        #Make .7 for good-ish clues
        if max(scores3) > .7:
            max_score = max(scores3)
        #Make .5 for good-ish clues
        elif max(scores2) > .5:
            max_score = max(scores2)
        else:
            max_score = max(scores1)

        scores1 = [0]
        scores2 = [0]
        scores3 = [0]

        for clue in possible_clues:
            if clue[1] == 1 and clue[0][1] != max_score:
                scores1.append(clue[0][1])
            if clue[1] == 2 and clue[0][1] != max_score:
                scores2.append(clue[0][1])
            if clue[1] == 3 and clue[0][1] != max_score:
                scores3.append(clue[0][1])

         #Make .75 for sensible clues
        if max(scores3) > .75:
            max2_score = max(scores3)
        #Make .5 for sensible clues
        elif max(scores2) > .5:
            max2_score = max(scores2)
        else:
            max2_score = max(scores1)

        clues = []
        for clue in possible_clues:
            if max_score == clue[0][1]:
                clues.append(clue)
            if max2_score == clue[0][1]:
                clues.append(clue)
        return clues

    #Forward search algorithm
    def get_best_clue(self, top2_clues):

        if len(top2_clues) == 1:
            return top2_clues[0]
        
        the_scores = []
        for top_clue in top2_clues:
            
            G_words_temp = []
            for word in self.G_words:
                if word != top_clue[0][0]:
                    G_words_temp.append(word)
                    
            if not G_words_temp:
                the_scores.append(1)
                break
            
            combos = []
        
            combos.extend(list(combinations(G_words_temp, 1)))
            if(len(self.G_words) >= 2):
                combos.extend(list(combinations(G_words_temp, 2)))
            if(len(self.G_words) >= 3):
                combos.extend(list(combinations(G_words_temp, 3)))
    
            #Don't check for assassin words here    
            for combo in combos:
                if len(combo) == 1:
                    vec = model[combo[0]] #\
                    #- model[self.R_words[0]] - model[self.R_words[1]] - model[self.R_words[2]]
                elif len(combo) == 2:
                    vec = model[combo[0]] + model[combo[1]] #\
                    #- model[self.R_words[0]] - model[self.R_words[1]] - model[self.R_words[2]]
                elif len(combo) == 3:
                    vec = model[combo[0]] + model[combo[1]] + model[combo[2]] #\
                    #- model[self.R_words[0]] - model[self.R_words[1]] - model[self.R_words[2]]
                
                similar = model.most_similar([vec])
                num = len(combo)    

                #To see which words the AI is giving the clue for
                clue_words = []
                for i in range(num):
                    clue_words.append(combo[i])
                
                words_lower = []
                for word in self.words:
                    words_lower.append(word.lower())

                #Check if it is a valid clue  
                for clue in similar:     
                    if clue[0] not in words_lower:
                        valid = True

                        #Doesn't contain any board words
                        for word in words_lower:
                            if word in clue[0].lower():
                                valid = False
                                break
                        
                        #Wasn't  previously given
                        for word in self.given_clues:
                            if clue[0].lower() in word.lower():
                                valid = False
                                break
                        
                        #Isn't similar to assassin words
                        for word in self.R_words:
                            vec = model[word]
                            similar = model.most_similar([vec], topn=200)
                            for similar_tuple in similar:
                                similar_word = similar_tuple[0]
                                if clue[0].lower() in similar_word or similar_word in clue[0].lower():
                                    valid = False
                                    break
                        
                        if valid:
                            #Add clue_words here to show which words the AI is giving the clue for
                            the_clue = [clue, num]
                        
                            possible_clues.append(the_clue)
                            break
            
            scores = [0]

            for clue in possible_clues:
                scores.append(clue[0][1])
                
            the_scores.append(max(scores))
            
        try:
            if the_scores[0] < the_scores[1]:
                return top2_clues[1]
            else:
                return top2_clues[0]
        except:
            return top2_clues[0]
        
if __name__  == '__main__':
    
    #random.seed(10)
    word_files = ('words/bruce.txt',)
    words = get_words(word_files)
    b = Board(words)
    s = Spymaster()
    s.add_words(words, b.colors)
    
    game = True
    turn = 0

    #Shows assassin words
    #print(s.R_words)
    
    while game:
        turn += 1
        print('Turn {}:'.format(turn))
        print(b)
        possible_clues = s.get_possible_clues()
        top2_clues = s.get_top2_clues(possible_clues)
        clue = s.get_best_clue(top2_clues)
        print('Your clue is: ')
        print(clue)
        print('')
        s.given_clues.append(clue[0][0])

        while True:
            guess = input('Guess now (or done): ')
            if guess.lower() == 'done':
                time.sleep(1)
                break
            else:
                if guess.upper() in b.words:
                    b.guesses.append(guess.upper())
                    word_index = b.words.index(guess.upper())
                    print(word_index)
                    print(b.colors[word_index])
                    if (b.colors[word_index] == 'G'):
                        print('Correct!\n')
                        try: s.G_words.remove(guess.lower())
                        except: pass
                        if not s.G_words:
                            print("You win!")
                            game = False
                            break
                        time.sleep(1)
                        print(b)
                    elif (b.colors[word_index] == 'Y'):
                        print('Civilian word!\n')
                        time.sleep(1)
                        break
                    elif (b.colors[word_index] == 'R'):
                        print('Assassin! You lose.\n')
                        time.sleep(1)
                        game = False
                        break
