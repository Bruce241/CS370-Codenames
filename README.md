# Codenames AI Project
This project was created for CS370 - Intro to Artificial Intelligence. \
I used a word2vec model that was trained using part of Google News dataset (about 100 billion words). The model contains 300-dimensional vectors for 3 million words and phrases. \

For the spymaster AI, I used a forward search algorithm:
  - First, I find the top two clues the AI could give out of all of the different combinations of size 1-3. These clues avoid the "assassin" words by making sure the clues are not similar to any of the "assassin" words.
  - Then, I take both of those clues and predict what their next top clue would be. Based on the best clue out of those two, I return to the original two clues and pick the one with the better folowing clue.
  - This continues until the game is over. The game ends once the player guesses all the correct words (and wins) or one of the assassin words (and loses).
