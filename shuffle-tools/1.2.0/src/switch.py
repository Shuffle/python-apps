# self, sourcevalue, condition, destinationvalue
def validate_condition(sourcevalue, check, destinationvalue):
    if check == "=" or check == "==" or check.lower() == "equals":
        if str(sourcevalue).lower() == str(destinationvalue).lower():
            return True
    elif check == "!=" or check.lower() == "does not equal":
        if str(sourcevalue).lower() != str(destinationvalue).lower():
            return True
    elif check.lower() == "startswith":
        if str(sourcevalue).lower().startswith(str(destinationvalue).lower()):
            return True


    elif check.lower() == "endswith":
        if str(sourcevalue).lower().endswith(str(destinationvalue).lower()):
            return True
    elif check.lower() == "contains":
        if destinationvalue.lower() in sourcevalue.lower():
            return True

    elif check.lower() == "is empty" or check.lower() == "is_empty":
        try:
            if len(json.loads(sourcevalue)) == 0:
                return True
        except Exception as e:
            print("[ERROR] Failed to check if empty as list: {e}")

        if len(str(sourcevalue)) == 0:
            return True

    elif check.lower() == "contains_any_of":
        newvalue = [destinationvalue.lower()]
        if "," in destinationvalue:
            newvalue = destinationvalue.split(",")
        elif ", " in destinationvalue:
            newvalue = destinationvalue.split(", ")

        for item in newvalue:
            if not item:
                continue

            if item.strip() in sourcevalue:
                return True
                    
    elif check.lower() == "larger than" or check.lower() == "bigger than" or check == ">" or check == ">=":
        try:
            if str(sourcevalue).isdigit() and str(destinationvalue).isdigit():
                if int(sourcevalue) > int(destinationvalue):
                    return True

        except AttributeError as e:
            print("[WARNING] Condition larger than failed with values %s and %s: %s" % (sourcevalue, destinationvalue, e))

        try:
            destinationvalue = len(json.loads(destinationvalue))
        except Exception as e:
            print("[WARNING] Failed to convert destination to list: {e}")
        try:
            # Check if it's a list in autocast and if so, check the length
            if len(json.loads(sourcevalue)) > int(destinationvalue):
                return True
        except Exception as e:
            print("[WARNING] Failed to check if larger than as list: {e}")


    elif check.lower() == "smaller than" or check.lower() == "less than" or check == "<" or check == "<=":
        print("In smaller than check: %s %s" % (sourcevalue, destinationvalue))

        try:
            if str(sourcevalue).isdigit() and str(destinationvalue).isdigit():
                if int(sourcevalue) < int(destinationvalue):
                    return True

        except AttributeError as e:
            pass

        try:
            destinationvalue = len(json.loads(destinationvalue))
        except Exception as e:
            print("[WARNING] Failed to convert destination to list: {e}")

        try:
            # Check if it's a list in autocast and if so, check the length
            if len(json.loads(sourcevalue)) < int(destinationvalue):
                return True
        except Exception as e:
            print("[WARNING] Failed to check if smaller than as list: {e}")

    elif check.lower() == "re" or check.lower() == "matches regex":
        try:
            found = re.search(str(destinationvalue), str(sourcevalue))
        except re.error as e:
            return False
        except Exception as e:
            return False

        if found == None:
            return False

        return True
    else:
        print("[DEBUG] Condition: can't handle %s yet. Setting to true" % check)

    return False

def evaluate_conditions(condition_structure):
    operator = condition_structure.get('operator')
    
    # Base case: Single condition
    if 'source' in condition_structure:
        source = condition_structure['source']
        condition = condition_structure['condition']
        destination = condition_structure['destination']

        # self.
        return validate_condition(source, condition, destination)
    
    # Recursive case: Logical operator
    elif operator == "AND":
        return all(evaluate_conditions(sub_condition) for sub_condition in condition_structure['conditions'])
    
    elif operator == "OR":
        return any(evaluate_conditions(sub_condition) for sub_condition in condition_structure['conditions'])
    
    elif operator == "NOT":
        return not evaluate_conditions(condition_structure['conditions'][0])

    else:
        raise ValueError(f"Unknown operator: {operator}")


def switch(conditions):
    to_return = {
        "success": True,
        "run_else": True,
    }

    for condition in conditions:
        if "id" not in condition:
            print("Condition ID not found")
            continue

        evaluated = False
        try:
            evaluated = evaluate_conditions(condition)
        except Exception as e:
            print(f"Failed to evaluate condition {condition['id']}: {e}")

        if evaluated == True:
            to_return["run_else"] = False

        to_return[condition["id"]] = evaluated

    return to_return

# Example usage

condition_structure = {
  "id": "lol",
  "operator": "AND",
  "conditions": [
    { # true
      "source": "20", # age
      "condition": ">",
      "destination": 18
    },
    { # true
      "operator": "OR",
      "conditions": [
        {
          "source": "active", # status
          "condition": "==",
          "destination": "active"
        },
        {
          "source": "1500", # balance
          "condition": ">=",
          "destination": 1000
        }
      ]
    },
    {
      "operator": "NOT",
      "conditions": [
        {
          "source": "user", # user
          "condition": "==",
          "destination": "admin"
        }
      ]
    }
  ]
}

newcondition = condition_structure.copy()
testconditions = [condition_structure]
newcondition['id'] = "lol2" 
testconditions.append(newcondition)

result = switch(testconditions)
print()
print()
print("Output: ", result)
