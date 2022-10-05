function candidateList() {
  this.list = [];
  this.addCandidate = function (candidate) {
    this.list.push(candidate);
  };

  this.eraseCandidate = function (candidate) {
    this.list.pop(candidate);
  };

  this.searchCandidate = function (candidate) {
    this.list.filter((element) => {
      return element == candidate;
    });
  };

  this.updateCandidate = function (candidate) {};
}
