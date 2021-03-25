function calculateAge(yearOfBirth) {
  let date = new Date();
  let year = date.getFullYear();
  return year - yearOfBirth;
}

console.log(calculateAge(2001));