Human Generated Art Verified by other humans 

This paper will attempt to explain exactly how HGAVBOH actually works, this is an aid not only for my implementation but also so that other users can understand what is going on behind the GUI application.

Primitives 

The first version of HGAVBOH assumes a trusted server that will read and serialize votes and award tokens for humanness. This trusted Server also produces new blockhashes acting as if it is the blockchain. 

Beyond this HGAVBOH makes standard crypto assumptions and just uses ED25519 keys for singing and verification of images and a Commit reveal scheme. 

The Idea 

Computers should find it hard to relate a number of unrelated words and draw a picture that looks like it was produced by a human. However the production of these images cannot be easily verified by computers unlike a CAPTCHA. Hence we require that when an image is produced the human that produces that image must also vote on another image and decide its humanness. In this vein we have a self repeating system where humans produce artworks and also verify other artworks. We hope that these two measures are extremely hard for a computer to master. And can produce valid proofs of humanness

How it actually works

Word Choice

The first thing a client should do is create its own drawing using the provided words shown to it. Functionally we generate random words by. 

Generating a random nonce, concatenating that random nonce with the current blockhash, hashing the result of this concatenation and using the result of that hash to seed a PRNG that picks 6 words from a list of ~1700 concrete nouns. 

The result of this is a fairly unpredictable word list, and although a user can quickly get new lists by using a new nonce, it is fairly hard for them to choose the outcome of words that they want, for example if a hashing algorithm like RandomX was used we can assume the average user will be able to generate about 8000 new word choices every second. 

If we assume the block hash changes unpredictability every 10 minutes then we can see the maximum amount of hashing that can be done by a client is  480,000 hashes per round, considering that with a word list of ~1700 words and 6 words chosen from that list there is a possible 32,300,953,973,338,600 (32 Quadrillion) combinations of those words, so using this technique insures that even a powerful attacker cannot choose their combinations of words. This ensures people cannot choose “Easy” word combinations which logically make more sense to a computer or human to draw. 

Additional to this since HGAVBOH also uses a blockchain each nonce + blockhash combos are stored and the resulting word choices can never be used again, this ensures images cannot be stolen and recycled in different rounds for the same word choices, although this is unlikely. 

Why 6 Words 

6 words was chosen as it represents a medium between being too hard for humans to relate and draw a meaningful drawing of and providing strong security against being able to simply choose which words you want to use. If it is found that computers can arrange and draw these words we could increase the number of words thus increasing the complexity of the drawings.

Safety against stealing 

Commit 

Reveal 


Simplified Full process in V1 

Client generates a long term ed25519 keypair which is stored on disk
Client generates words by concternating nonce with blockhash hashing the result and feeding it as the seed to a PRNG which chooses words from a word list 
Client draws a picture related to those words, when finished they click the save button 
When the save button is clicked this initiates the process of packing the image, packing the image means the raw image bytes + a timestamp + a hash of the image and the current blockhash is all signed by the long term ed25519 key
Client will then switch to the voting mode, the client checks the vote pool and chooses the three oldest images by timestamp which have not been voted on at least three times. These images fetched from the trusted server are then displayed, the client must decide whether that images displayed are produced by a human or not.
Once the client has voted, they produce a commit, which includes a commit nonce + a commit timestamp + the decisions + the image hashes of the target images they voted on. This data is conceternated and then hashed together, and added to the packed image 
This data is then submitted to the trusted server, this is the commit round
Other clients progressively poll the trusted server for new commits and load this data into their own clients, verifying the signature matches the submitted data and the hashed raw bytes are the same as the image hash.
After 30 seconds the reveal is made by the client, the reveal contains a the imagehash of the original image + the original image nonce + the commit timestamp + the commit nonce + the commit decisions + the commit Vote targets + a signature from the longterm ed25519 key. 
At the same time the client also submits votes to the Server, these votes contain some plaintext data which shows the origin image + the vote target + the decision and a signature from the longterm ed25519 keys  
Reveal data is loaded by each client and checked against each fetched image until a match between the original image hash is found with an image already in the database. When a match is found the reveal data is concatenated and hashed, if the hash matches with the committed data and the signature is valid then we consider this a true image.
True images are loaded to other clients verification screens to be voted on

Server Side Logic 

Server triggers vote recounting anytime a new vote is uploaded to the server
When a vote arrives it is compared against the origin imagehashes of all of the revealed images if a match is found we proceed to validate that the signature for the vote is produced by the same key in the reveal and that the signature is valid
If this is valid then the vote is added to the pool of real votes 
Each time a new vote is added to the pool of votes the server runs a selection process, if any image has over 3 votes which come from different imagehashes then the image is approved aslong as it own vote will be in consensus when released 

Possible Attacks 


Writing Messages in Pictures 

Since pictures are required to be produced and verified by other humans we could see computers writing text messages in images. Text is extremely easy for computers to generate, these text messages do not follow the spirit of the tool, to ensure these messages do not get marked we will need to educate the user that they should not verfiy images with text inside

Reusing images with similar words

It is feasible that someone could scrape images from the public database of artworks that were verified to match other word combinations and reuse those images for other cobinations of words. 

For example if i have an artwork which was verified for the words 

Dog Bread Cake Pig Rocky Mask 

Then i may be able to, through hashing produce a 4 word combination or words like 

Cake Mask Pig Dog Tattoo Locker 

There is a potential that if i submit this image, even though it only matches 4 out of the 6 words it will still be verified, it is for this reason that we need to educate users that when they are verfying images all 6 words must match what is stated in the word list. 


