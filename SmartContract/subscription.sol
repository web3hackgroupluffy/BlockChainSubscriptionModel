// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

contract SubscriptionManager {
    struct Subscription {
        address user;
        uint256 endTime;
    }

    uint256 public constant subscriptionFee = 1 ether;
    uint256 public constant subscriptionDuration = 2 minutes;

    // Mapping of user addresses to their list of subscriptions
    mapping(address => Subscription[]) public userSubscriptions;

    // Mapping of creator addresses to their list of subscribers
    mapping(address => Subscription[]) public creatorSubscribers;

    event Subscribed(address indexed user, address indexed creator, uint256 endTime);

    function subscribe(address creator) external payable {
        require(msg.sender != creator, "Cannot subscribe to oneself");
        require(msg.value == subscriptionFee, "Incorrect subscription fee");
        require(!isSubscribed(msg.sender, creator), "Already subscribed");

        // Add the subscription to the user's list
        userSubscriptions[msg.sender].push(Subscription({
            user: creator,
            endTime: block.timestamp + subscriptionDuration
        }));

        // Add the user to the creator's list of subscribers
        creatorSubscribers[creator].push(Subscription({
            user: msg.sender,
            endTime: block.timestamp + subscriptionDuration
        }));

        // Transfer the subscription fee to the creator
        payable(creator).transfer(msg.value);

        emit Subscribed(msg.sender, creator, block.timestamp + subscriptionDuration);
    }

    function getSubscriptions(address user) external view returns (Subscription[] memory) {
        return userSubscriptions[user];
    }

    function getSubscribers(address creator) external view returns (Subscription[] memory) {
        return creatorSubscribers[creator];
    }

    function isSubscribed(address user, address creator) public view returns (bool) {
        Subscription[] memory subscriptions = userSubscriptions[user];
        for(uint i = 0; i < subscriptions.length; i++) {
            if(subscriptions[i].user == creator && subscriptions[i].endTime > block.timestamp) {
                return true;
            }
        }
        return false;
    }
}
