import postsandgets

#This will periodically scan the vote pool and assign tokens based on voting 
#It should not need to know anything else other than votes since votes are self validates by other users votes and cant be faked

votelist = postsandgets.getVotelist()
votes = postsandgets.getVotes(voteList)