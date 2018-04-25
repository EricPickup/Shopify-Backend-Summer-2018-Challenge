#Eric Pickup
#January 11th, 2018
#Shopify Summer 2018 Back-End Internship Challenge

import urllib.request, json 
from collections import defaultdict
import math

'''
Function: traverseTree
Description: Recursively traverses the tree, recording each node visited to ensure that there are no cycles
Input: ID of the initial item to traverse from
Output: 1 if proper menu, -1 if cycle is found
'''
def traverseTree(itemID):

	#===Base cases========
	#1) Leaf node (no children)
	if not menu[itemID].children:
		visited[itemID] = 1
		return 1

	#2) Found duplicate item ID (already seen, meaning there is a cycle)
	if visited[itemID] == 1:
		return -1
	#=====================

	#Mark item as visited
	visited[itemID] = 1

	cycleFoundFlag = 0
	
	#For each child of the current node:
	for i in menu[itemID].children:
		#Recursively traverse children of current node and return -1 if a cycle is found
		if (traverseTree(i) == -1):
			cycleFoundFlag = 1
	if cycleFoundFlag:
		return -1
	return 1


class menuItem:
	def __init__(self, id, data, parentID, children):
		self.id = id
		self.data = data
		self.parentID = parentID
		self.children = children



#===================================== 	DATA RETRIEVAL 	====================================================

#Dictionary containing all menu items from JSON, key = menuID, value = menuItem object
menu = defaultdict(list)

rootIDs = []
numPages = 1
i = 1

#Loop for every page
while i <= numPages:

	#Retrieving json info for current page
	urlString = "https://backend-challenge-summer-2018.herokuapp.com/challenges.json?id=2&page=" + str(i)
	url = urllib.request.urlopen(urlString)
	data = json.loads(url.read().decode())

	#Calculate total number of pages
	numPages = math.ceil(data["pagination"]["total"] / data["pagination"]["per_page"])

	#For every menu item retrieved from the current page
	for currentItem in data["menus"]:

		#If the node has a parent (inner/leaf node), create a menuItem object and store it in the dict of items
		if "parent_id" in currentItem:
			menu[currentItem["id"]] = menuItem(currentItem["id"], currentItem["data"], currentItem["parent_id"], currentItem["child_ids"])

		#Otherwise, it is a root node - create menuItem object and store it in menu dict - also store ID of this root to keep track of all separate graphs
		else:
			menu[currentItem["id"]] = menuItem(currentItem["id"], currentItem["data"], -1, currentItem["child_ids"])
			rootIDs.append(currentItem["id"])

	i += 1

#==============================	CYCLE SEARCH AND STORING RESULTS IN JSON FORMAT ============================

data = {}
data['valid_menus'] = []
data['invalid_menus'] = []

#For every root node (separate tree)
for currentRoot in rootIDs:

	#Keep track of each node we've visited - if the node is visited more than once, a cycle exists
	visited = defaultdict(list)

	#If no cycle is found when traversing the current tree, store in valid_menus
	if (traverseTree(currentRoot) == 1):
		del visited[currentRoot]	#First node in child list will be the root (isn't a child)
		data['valid_menus'].append({
			'root_id': currentRoot,
			'children': list(visited.keys())
			})

	#Otherwise, a cycle has been found. Store in invalid_menus
	else:
		data['invalid_menus'].append({
			'root_id': currentRoot,
			'children': list(visited.keys())
			})

#Print final results
print(json.dumps(data,indent=2))