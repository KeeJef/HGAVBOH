import postsandgets

#This will periodically scan the vote pool and assign tokens based on voting 
#It should not need to know anything else other than votes since votes are self validates by other users votes and cant be faked

votelist = postsandgets.getVotelist()
votes = postsandgets.getVotes(votelist)

#traverse the data in a nested for loop, when you reach a vote, create an object for that image and assign the vote
# once this is finised loop through the objects created and sign and encrypt(this maybe a little tricky (put pub key in votes?)) tokens for the image public key
#If singed token is presented then we know it worked

pass