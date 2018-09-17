class GSP(object):

    def __init__(
            self,
            startState,
            goalState,
            actionStore,
            ss,
            gg,
            blocklist=['A', 'B', 'C', 'D']
    ):

        self.counter = 0
        self.blockList = blocklist
        self.startState=self.state_2_conjunct(ss)
        self.goalState=self.state_2_conjunct(gg)
        self.actionStore=actionStore






    def generateConjunct(self, preCondList, args):
        c = []
        for p in preCondList:
            t = []
            t.append(p[0])
            for a in p[1:]:
                # print a
                t.append(args[int(a[1])])
            t1 = tuple(t)
            c.append(tuple(['predicate', t1]))
        return tuple(['conjunct', c])


    def generate_and_set_blocks_list(self, state):
        bList = set()
        on = state['on']
        for t in on:
            bList = bList.union(list(t))

        bList = bList.union(state['onTable'] + state['holding'] + state['clear'])
        self.blockList = list(bList)
        return bList


    def plan_to_states_list(self, plan, start):
        out = []
        state = start
        s = self.conjunct_2_state(state)
        out.append(s)

        for action in plan:
            state = self.progress(state, action)
            s = self.conjunct_2_state(state)
            out.append(s)

        return out


    def progress(self, state, action):
        # sanity checks have been assumed
        # ie the fact that the action _can_ be done is assumed by this function
        currentState = self.conjunct_2_state(state)
        name = action[1][0]
        args = action[1][1:]

        add = self.actionStore[name]['A']
        for a in add:
            if a[0] == 'on':  # two args, put as tuple
                currentState[a[0]].append(tuple([args[int(a[1][1])], args[int(a[2][1])]]))
            elif a[0] == 'armEmpty':
                currentState[a[0]] = True
            else:  # one arg
                currentState[a[0]].append(args[int(a[1][1])])

        delete = actionStore[name]['D']
        for d in delete:
            if d[0] == 'on':
                currentState[d[0]].remove(tuple(args))
            elif d[0] == 'armEmpty':
                currentState[d[0]] = False
            else:
                currentState[d[0]].remove(args[int(d[1][1])])

        return self.state_2_conjunct(currentState)


    # return only a _list_ of actions and no conjuncts
    def get_actions_for_predicate(self, pred):
        p = pred[1]
        name = p[0]
        args = p[1:]
        actions = []
        if name == 'on':
            actions = [('action', ('stack', args[0], args[1]))]

        elif name == 'onTable':
            actions = [('action', ('putDown', args[0]))]

        elif name == 'clear':

            for b in self.blockList:
                if b != args[0]:
                    actions.append(('action', ('stack', args[0], b)))
            for b in self.blockList:
                if b != args[0]:
                    actions.append(('action', ('unStack', b, args[0])))

        elif name == 'holding':

            actions.append(('action', ('pickup', args[0])))
            for b in self.blockList:
                if b != args[0]:
                    actions.append(('action', ('unStack', args[0], b)))

        elif name == 'armEmpty':

            for b in self.blockList:
                actions.append(('action', ('putDown', b)))

            for b1 in self.blockList:
                for b2 in self.blockList:
                    if b1 != b2:
                        actions.append(('action', ('stack', b1, b2)))

        return actions


    def is_in_state(self, pred, state):
        return pred in state[1]
        p = pred[1]
        name = p[0]
        if name == 'on':
            return p[1:] in state[name]
        elif name == 'armEmpty':
            return state[name]
        else:
            return p[1:] in state[name]


    def check_sovled(self, predList, state):
        for p in predList:
            if not self.is_in_state(p, state):
                return False
        return True


    # convert from state dict to a conjuct form
    def state_2_conjunct(self, state):
        conjunct = []

        if state['onTable']:
            for t in state['onTable']:
                p = ['predicate', ]
                o = ['onTable', ]
                o.append(t)
                p.append(tuple(o))
                conjunct.append(tuple(p))

        if state['clear']:
            for t in state['clear']:
                p = ['predicate', ]
                o = ['clear', ]
                o.append(t)
                p.append(tuple(o))
                conjunct.append(tuple(p))

        if state['holding']:
            for t in state['holding']:
                p = ['predicate', ]
                o = ['holding', ]
                o.append(t)
                p.append(tuple(o))
                conjunct.append(tuple(p))

        if state['armEmpty']:
            p = ['predicate', ]
            o = ['armEmpty', ]
            p.append(tuple(o))
            conjunct.append(tuple(p))

        if state['on']:
            for t in state['on']:
                p = ['predicate', ]
                o = ['on', ]
                o.extend(t)
                p.append(tuple(o))
                conjunct.append(tuple(p))

        return tuple(['conjunct', conjunct])

    def conjunct_2_state(self, conjunct):
        state = {
            'on': [],
            'onTable': [],
            'clear': [],
            'holding': [],
            'armEmpty': False
        }
        for c in conjunct[1]:
            a = c[1]
            if a[0] == 'on':
                state['on'].append(a[1:])
            elif a[0] == 'onTable':
                state['onTable'].append(a[1])
            elif a[0] == 'clear':
                state['clear'].append(a[1])
            elif a[0] == 'holding':
                state['holding'].append(a[1])
            elif a[0] == 'armEmpty':
                state['armEmpty'] = True
        return state


    def gsp_recursive(self, state, goal, openList):  # return plan, new-state
        plan = []
        g_type = goal[0]
        self.counter += 1
        print('GOAL: ', goal)
        # print state
        if g_type == 'conjunct':
            predList = goal[1]
            ## print predList
            if not self.check_sovled(predList, state):
                plan1, state1 = [], state
                for p in predList:
                    ## print p
                    g = self.gsp_recursive(state1, p, openList)
                    if g:
                        plan1, state1 = g
                        plan.extend(plan1)
                    else:

                        # # print goal
                        self.counter -= 1

                        return False

                if not self.check_sovled(predList, state1):
                    change = True
                    while change:
                        for p in predList:
                            if not self.is_in_state(p, state1):
                                g = self.gsp_recursive(state1, p, openList)
                                if g:
                                    plan1, state1 = g
                                    plan.extend(plan1)
                                    break  # changed, start over
                                else:
                                    # we need a better way to handle this.
                                    return False
                        else:
                            change = False
                    # all solved, peace
                self.counter -= 1

                return plan, state1

            else:  # if all are already solved
                self.counter -= 1

                return [], state

        else:  # goal is a predicate
            if self.is_in_state(goal, state):
                self.counter -= 1

                return [], state
            elif goal in openList:
                self.counter -= 1

                return False
            else:
                openList.append(goal)
                actions = self.get_actions_for_predicate(goal)
                plan1, state1 = [], state

                for a in actions:
                    name = a[1][0]
                    args = a[1][1:]
                    precondList = self.actionStore[name]['P']
                    conjunct = self.generateConjunct(precondList, args)

                    g = self.gsp_recursive(state1, conjunct, openList)
                    if g:
                        plan1, state1 = g
                        plan1.append(a)
                        self.counter -= 1
                        rr = plan1, self.progress(state1, a)

                        return rr
                    else:
                        continue
                else:
                    self.counter -= 1
                    return False


# print(json.dumps(ss))
# sys.exit()

startState = {
    'on': [],
    'onTable': ['A', 'B'],
    'clear': ['A', 'B'],
    'holding': [],
    'armEmpty': True
}
goalState = {
    'on': [('B', 'A')],
    'onTable': ['A'],
    'clear': ['B'],
    'holding': [],
    'armEmpty': True
}

actionStore = {
    'pickup': {
        'P': [('onTable', '_0'), ('clear', '_0'), ('armEmpty',)],
        'A': [('holding', '_0')],
        'D': [('onTable', '_0'), ('armEmpty',)]
    },

    'putDown': {
        'P': [('holding', '_0')],
        'A': [('onTable', '_0'), ('armEmpty',)],
        'D': [('holding', '_0')]
    },

    'unStack': {
        'P': [('on', '_0', '_1'), ('clear', '_0'), ('armEmpty',)],
        'A': [('holding', '_0'), ('clear', '_1')],
        'D': [('on', '_0', '_1'), ('armEmpty',)]
    },
    'stack': {
        'P': [('holding', '_0'), ('clear', '_1')],
        'A': [('on', '_0', '_1'), ('clear', '_0'), ('armEmpty',)],
        'D': [('holding', '_0'), ('clear', '_1')]
    }
}



def conjunct_2_state(conjunct):
    state = {
        'on': [],
        'onTable': [],
        'clear': [],
        'holding': [],
        'armEmpty': False
    }
    for c in conjunct[1]:
        a = c[1]
        if a[0] == 'on':
            state['on'].append(a[1:])
        elif a[0] == 'onTable':
            state['onTable'].append(a[1])
        elif a[0] == 'clear':
            state['clear'].append(a[1])
        elif a[0] == 'holding':
            state['holding'].append(a[1])
        elif a[0] == 'armEmpty':
            state['armEmpty'] = True
    return state


ss = {
    'on': [('B', 'A'), ],
    'onTable': ['A', 'C', 'D'],
    'clear': ['B', 'C', 'D'],
    'holding': [],
    'armEmpty': True
}

gg = {
    'on': [('C', 'A'), ('B', 'D')],
    'onTable': ['A', 'D'],
    'clear': ['C', 'B'],
    'holding': [],
    'armEmpty': True
}
ss = {
    'on': [('B', 'A'),],
    'onTable': ['A', 'C', 'D'],
    'clear': ['B', 'C', 'D'],
    'holding': [],
    'armEmpty': True
}

gg = {
    'on': [('C', 'A'),],
    'onTable': ['A', 'D', 'B'],
    'clear': ['A', 'B', 'D'],
    'holding': [],
    'armEmpty': True
}

ss = {
    'on': [('C', 'A'), ('A', 'B')],
    'onTable': ['B'],
    'clear': ['C'],
    'holding': [],
    'armEmpty': True
}

gg = {
    'on': [],
    'onTable': ['A', 'B', 'C', ],
    'clear': ['A', 'B', 'C'],
    'holding': [],
    'armEmpty': True
}

gsp = GSP(startState=startState, goalState=goalState, actionStore=actionStore, ss=ss, gg=gg)
plan, state = gsp.gsp_recursive(gsp.startState, gsp.goalState, [])
# plan, state = gsp_recursive(s, g, [])
state = conjunct_2_state(state)

print('STATE', state)