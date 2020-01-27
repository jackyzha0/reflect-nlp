# -- Data Processing Imports --
import matplotlib.pyplot as plt  # graphing
import numpy as np  # more data processing stuff
import pandas as pd  # data processing/analysis

# -- Deep Learning Libraries --
from keras.callbacks import EarlyStopping
from keras.optimizers import RMSprop
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# -- Local imports --
import net
import data_proc

# -- Params --
TOKENIZER_VOCAB_SIZE = 500
SEQUENCE_MAX_LENGTH = 75
BATCH_SIZE = 64
NUM_EPOCHS = 100
TRAIN_TEST_SPLIT = 0.15
VALIDATION_SPLIT = 0.1

# Load survey info
print('Loading Dataframe')
df = pd.read_csv('data/survey.csv', sep="\t",
                 header=None, names=["intent", "valid"])
print('Number of invalid intents: %d' % len(df[df.valid == 'no']))
print('Number of valid intents: %d' % len(df[df.valid == 'yes']))

# Map labels
df['valid'] = df.valid.map({'no': 0, 'yes': 1})
print('-- Some sample labels --')
print(df.valid.tail(5))

# Clean text
numPunc = df.intent.apply(data_proc.countPunctuation)
df['intent'] = df.intent.apply(data_proc.stripPunctuation)

numCaps = df.intent.apply(data_proc.countCaps)
df['intent'] = df.intent.apply(data_proc.stripCaps)
df['intent'] = df.intent.apply(data_proc.rmPersonalPrefix)
print('-- Some sample intents --')
print(df.intent.tail(5))

# create X (input) and Y (expected)
X = df.intent
Y = df.valid

# create new Label encoder
labelEncoder = LabelEncoder()
Y = labelEncoder.fit_transform(Y)
Y = Y.reshape(-1, 1)
# output is now one hot encoded

# Train/Test split, 15% test set
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=TRAIN_TEST_SPLIT)

# Data processing
tokenizer = Tokenizer(num_words=TOKENIZER_VOCAB_SIZE)
tokenizer.fit_on_texts(X_train)
seqs = tokenizer.texts_to_sequences(X_train)
padded_seqs = sequence.pad_sequences(
    seqs, maxlen=SEQUENCE_MAX_LENGTH, padding='post')

# Load Network Architecture
model = net.RNN(SEQUENCE_MAX_LENGTH, TOKENIZER_VOCAB_SIZE)
model.summary()
model.compile(loss='binary_crossentropy',
              optimizer=RMSprop(), metrics=['accuracy'])

# Model Training
model.fit(padded_seqs, Y_train, batch_size=BATCH_SIZE, epochs=NUM_EPOCHS,
          validation_split=VALIDATION_SPLIT)


test_seqs = tokenizer.texts_to_sequences(X_test)
padded_test_seqs = sequence.pad_sequences(
    test_seqs, maxlen=SEQUENCE_MAX_LENGTH)
accr = model.evaluate(padded_test_seqs, Y_test)
print('Test set\n  Loss: {:0.3f}\n  Accuracy: {:0.3f}'.format(accr[0],accr[1]))

for intent in df.intent.sample(10):
	seq = tokenizer.texts_to_sequences([intent])
	padded_seq = sequence.pad_sequences(seq, maxlen=SEQUENCE_MAX_LENGTH)
	preds = model.predict(padded_seq)
	print(str(intent) + ' => ' + str(preds[0][0]))