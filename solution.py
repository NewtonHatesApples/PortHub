class Solution:
    def bmi(self, weight: float, height: float):
        if height == 0.0:
            return -1
        else:
            return weight / (height ** 2)


if __name__ == "__main__":
    answer = Solution().bmi(58, 1.73)
    print(answer)
