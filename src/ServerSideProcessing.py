import postsandgets

imagearray = []


#This will periodically scan the vote pool and assign tokens based on voting 
#It should not need to know anything else other than votes since votes are self validates by other users votes and cant be faked

class imageobj:
    imagehash =""
    voteTally = 0

def subvotetarget(subvote):

    for votecandidate in imagearray:

        if votecandidate.imagehash == subvote['voteForImageHash']:

            return votecandidate
            
        pass

    return

def classifyvote(subvote):
    votechange = 0
    if subvote["decision"] == True:
        votechange += 1
        pass
    else:
        votechange -= 1
        pass
    return votechange


votelist = postsandgets.getVotelist()
votes = postsandgets.getVotes(votelist)

for wholevote in votes:

    for subvote in wholevote:

        votetarget = subvotetarget(subvote)
        voteincrement = classifyvote(subvote)
        if votetarget:
            votetarget.voteTally += voteincrement
            pass
        else:
            image = imageobj()
            image.imagehash = subvote["voteForImageHash"]
            image.voteTally = voteincrement
            imagearray.append(image)
        pass

    pass

#traverse the data in a nested for loop, when you reach a vote, create an object for that image and assign the vote
# we need to check the signature matches the images pub key
# once this is finised loop through the objects created and sign and encrypt(this maybe a little tricky (put pub key in votes?)) tokens for the image public key
#If singed token is presented then we know it worked

#we will actually need to have both Real votes and Half votes, 
#half votes only become real votes when the origin image hash received X real votes

pass