# Brain Chain**

Submitted by: **BinaryBills, Kleptis, zakzak1248, hlee18lee46**

**Brain Chain** is Brain Chain is a subscription-based blockchain service for sharing academic documents, where users receive Ethereum when another user subscribes to them. Files are managed through an IPFS system.

## Features

Brain Chain is a subscription-based blockchain service tailored for students who want to share their lecture notes and documentation. Rather than paying for specific content, users subscribe directly to the creator of the notes, which provides a monetary value for students to be more engaged and contribute to academia. A user earns money when another user subscribes to them. The Blockchain stores all subscription data and access control, and IPFS stores the uploaded files. 

## How we built it
We used Python and Flask to handle our back end and used HTML, CSS and bootstrap to build the front end. We used Metamask for login, and IPFS for decentralized file storage.

## Challenges we ran into
We tried to use ipfshttpclient python library in the first place, but the library ipfshttpclient did not support the newer version of the ipfs. We installed the older version, but the older version could not be run because the repo version was not supported. Then, we figured out another way to interact with ipfs, which was using json and requests python library and directly interact with ipfs with them.

Another challenge was to find a way to deploy the project. We found out firebase was not an ideal choice for our flask app because it will not be static. 
Lastly, web 3.0 poor compatibility with Metamask made signing transactions difficult. 

## Video Walkthrough

Here's a walkthrough of implemented user stories:

<img src='https://i.imgur.com/KbLtXm5.gif' title='Video Walkthrough' width='' alt='Video Walkthrough' />

<!-- Replace this with whatever GIF tool you used! -->
GIF created with ScreenToGif   
<!-- Recommended tools:
[Kap](https://getkap.co/) for macOS
[ScreenToGif](https://www.screentogif.com/) for Windows
[peek](https://github.com/phw/peek) for Linux. -->




