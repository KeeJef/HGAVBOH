## Problem

CAPTCHAs (Completely Automated Public Turing tests to tell Computers and Humans Apart) were invented in the late 90s early 2000’s they have a few major issues 

- Generation and validation of a CAPTCHA requires a centralised trusted server.
- Machine Learning techniques are becoming increasingly good at solving CAPTCHA which brings their longevity into question.
- The most successful CAPTCHA’s now lend human brain power to single corporations to classify images with nothing of value produced for the solver.
- Solving a CAPTCHA in one place does not automatically exempt you from needing to solve CAPTCHA’s elsewhere

Therefore it is useful to create a new scheme to verify humanness for use in both decentralised networks and to act as a global humanness proof voucher for the internet. 

## Solution

Understanding natural human language, organising visual space, relating unrelated words and creating art are all things computers struggle to do in a way that looks human. These are all elements of the HGAVBOH (Human Generated Art Verified By Other Humans) system. The basic scheme is as follows. 

![Imgur](https://i.imgur.com/hGwP7Cv.png)

1. Generate an artwork based on 6 randomly selected concrete nouns, example above.
2. Download all the artworks waiting to be verified and secretly vote (Commit reveal) on which ones you think are human or computer generated, when vote you must also submit the artwork you just created.
3. Other artwork verifiers will view your artwork and vote, if a majority votes that your artwork was produced by a human then you earn some humanness vouchers and your votes on the other downloaded artworks are added to the network
4. Humanness vouchers are single use and are consumed by each application where you are required to prove your humanness
5. Humanness vouchers are tracked through a simple blockchain and can be bought and sold on secondary markets if the user does not want to generate their own artworks
