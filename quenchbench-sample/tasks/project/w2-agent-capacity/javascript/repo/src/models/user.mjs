export class User {
  // role is 'agent' or 'requester'; capacity is how many active tickets an agent should carry
  constructor(name, role = 'agent', skills = [], capacity = 5) {
    this.name = name;
    this.role = role;
    this.skills = skills;
    this.capacity = capacity;
  }
}
