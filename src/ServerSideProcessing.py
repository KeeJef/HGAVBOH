import postsandgets

imagearray = []
votesRequiredPerImage = 2


#This will periodically scan the vote pool and assign tokens based on voting 
#It should not need to know anything else other than votes since votes are self validates by other users votes and cant be faked

class imageobj:
    imagehash =""
    voteTally = 0

def subvotetarget(subvote):
    #return existing vote object if we have already created an object for that Target image
    for votecandidate in imagearray:

        if votecandidate.imagehash == subvote['voteForImageHash']:

            return votecandidate
            
        pass

    return

def classifyvote(subvote):
    #determine if the vote is for or agasint and assign a numerical value
    votechange = 0
    if subvote['decision'] == 'True':
        votechange += 1
        pass
    else:
        votechange -= 1
        pass
    return votechange

def backcheckvote(originimagehash):
    #we want to scan through all the votes looking for atleast threshold postive votes for the origin image hash
    votecount = 0

    for wholevote in votes:

        for subvote in wholevote:

            if subvote["voteForImageHash"] == originimagehash: #if the vote is for orgin image hash
                increment = classifyvote(subvote) #determines a vote for yes or no -1 for no +1 for yes
                votecount += increment
            pass

        pass
    
    if votecount < votesRequiredPerImage:
        return False    
    else:
        return True
        


votelist = postsandgets.getVotelist()
votes = postsandgets.getVotes(votelist)

for wholevote in votes:

    for subvote in wholevote:

        if backcheckvote(subvote['originImageHash']) == False: #Checks if we can count this vote as valid, to be valid it needs to have atleast 2 votes its self
            continue

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

    pass

for image in imagearray:
    print(image.imagehash +" "+ str(image.voteTally))
    pass



#traverse the data in a nested for loop, when you reach a vote, create an object for that image and assign the vote
# we need to check the signature matches the images pub key
# once this is finised loop through the objects created and sign and encrypt(this maybe a little tricky (put pub key in votes?)) tokens for the image public key
#If singed token is presented then we know it worked

#basically when we add a vote we want to check if the origin image hash has votes for it, if it does not have atleast vote threshold then we dont add the vote

#We need to create a real life vote dependency in which A1 is voted on by A2, and A3 and A2 and A3

