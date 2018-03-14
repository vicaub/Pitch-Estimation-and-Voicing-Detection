EXEC      = compare_pitch
SRC_FILES = compare_pitch.cpp

CC              = g++
DEBUG_LEVEL     = -O2

EXTRA_CCFLAGS   = -std=c++11 -MMD -MP -pthread
CXXFLAGS        = $(DEBUG_LEVEL) $(EXTRA_CCFLAGS)
CCFLAGS         = $(CXXFLAGS)
CPPFLAGS        =
LDFLAGS         =

O_FILES         = $(SRC_FILES:%.cpp=%.o)
D_FILES         = $(SRC_FILES:.cpp=.d)

all: $(EXEC)

$(EXEC): $(O_FILES)

clean:
	$(RM) $(O_FILES) $(D_FILES)

dist-clean: clean
	$(RM) $(EXEC)

-include $(D_FILES)
