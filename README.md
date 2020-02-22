![Imgur](https://i.imgur.com/y71NcC9.png)

## Decommissioned 

I've halted work on this project as i've realised that it has an unsolved Sybil attack problem, i thought this would be solved by having votes only be released when they had at least "threshold votes" , but during testing i realised that just kicks the problem down the road. The attack here would just to produce junk images with junk votes for your own images, even though your images won't be verified by other humans you can do this at scale and beat the other humans.  

## Problem

CAPTCHAs (Completely Automated Public Turing tests to tell Computers and Humans Apart) were invented in the late 90s early 2000’s they have a few major issues 

- Generation and validation of a CAPTCHA requires a centralised trusted server.
- Machine Learning techniques are becoming increasingly good at solving CAPTCHA which brings their longevity into question.
- The most successful CAPTCHA’s now lend human brain power to single corporations to classify images with nothing of value produced for the solver.
- Solving a CAPTCHA in one place does not automatically exempt you from needing to solve CAPTCHA’s elsewhere

Therefore it is useful to create a new scheme to verify humanness for use in both decentralised networks and to act as a global humanness proof voucher for the internet. 

## Solution

Understanding natural human language, organising visual space, relating unrelated words and creating art are all things computers struggle to do in a way that looks human. These are all elements of the HGAVBOH (Human Generated Art Verified By Other Humans) system. The basic scheme is as follows. 

1. Generate an artwork based on 6 randomly selected concrete nouns, example above.
2. Download all the artworks waiting to be verified and secretly vote (Commit reveal) on which ones you think are human or computer generated, when vote you must also submit the artwork you just created.
3. Other artwork verifiers will view your artwork and vote, if a majority votes that your artwork was produced by a human then you earn some humanness vouchers and your votes on the other downloaded artworks are added to the network
4. Humanness vouchers are single use and are consumed by each application where you are required to prove your humanness
5. Humanness vouchers are tracked through a simple blockchain and can be bought and sold on secondary markets if the user does not want to generate their own artworks

## Notes 

Note 1 

There is an issue with the current design where raw images could be sperated while flowing over the p2p network and stolen and submitted by other users as their own artworks. The issue here is that the nonce + the artwork are distributed together, instead it would be better to have a two phase submission

1. Hash the and sign the entire artwork, and flood it to the network
2. After you are sure the whole network knows the hash and public key who owns the artwork, then publish the nonce which generates the words for the verfication, this way no one can steal the raw artwork for their own submission since they need to know the nonce which generates valid words which that artwork is related with, and once you reveal the nonce everyone in the network already knows that artwork is yours

I think this could also occur alongside the commit reveal process of voting

Note 2

Word combinations should only ever be valid once, repetition of words should be tracked in the blockchain and and word combo that has already been used should be chucked

Note 3  

Image oldness is dertermined by user timestamp, which is insecure as people can jump the queue, should be determined by some recipent or server timestamp

