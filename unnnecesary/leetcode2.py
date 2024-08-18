class Solution:
    def findMedianSortedArrays(self, nums1: list[int], nums2: list[int]) -> float:
        merged_array = nums1 + nums2
        merged_array.sort()
        
        value = 0
    
        if len(merged_array)%2 == 1:
            median_value_loc = int(len(merged_array)/2)
            value = merged_array[median_value_loc]
        elif len(merged_array)%2 == 0:
            median_value_loc_1 = len(merged_array)/2 -1
            median_value_loc_2 = len(merged_array)/2
            value = (merged_array[median_value_loc_1] + merged_array[median_value_loc_2]) / 2
        
        return float(value)
        

if __name__ == '__main__':
    nums1 = [1,3]
    nums2 = [2]
    
    solution = Solution()
    
    print(solution.findMedianSortedArrays(nums1, nums2))
    