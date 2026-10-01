pragma solidity ^0.8.0;

contract Voting {
    mapping(address => bool) private hasRights;
    mapping(address => bool) private hasVoted;

    uint public approveCnt;
    uint public rejecCnt;
    uint public required;
    bool public ended;
    bool public approved;

    modifier available_vote() {
        require(!ended, "Voting ended.");
        require(hasRights[msg.sender], "Invalid address.");
        require(!hasVoted[msg.sender], "Already voted.");
        _;
    }

    constructor(address[] memory _voters) {
        for (uint i = 0; i < _voters.length; i++) {
            hasRights[_voters[i]] = true;
        }
        required = _voters.length / 2 + 1;
    }

    function voteApprove() public available_vote {
        hasVoted[msg.sender] = true;
        approveCnt++;

        if (approveCnt >= required) {
            ended = true;
            approved = true;
        }
    }

    function voteReject() public available_vote {
        hasVoted[msg.sender] = true;
        rejecCnt++;

        if (rejecCnt >= required) {
            ended = true;
            approved = false;
        }
    }
}
